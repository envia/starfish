#!/usr/bin/env python3
"""Single source of truth for the predicates that grade one source deep-link.

Two validators (``validate_grounding``, ``validate_wiki_claims``) and two repair
tools (``fix_citation_labels``, ``fix_deeplink_lines``) all reason about the same
markdown citations. Each used to
carry its own copy of the URL parsing, label classification and matching logic, and
the copies drifted apart — one axis caught what another silently passed (issues #29,
#31, #33). Every judgment about *one link* therefore lives here; the callers own only
which links are in scope, what gates the pipeline, and how results are aggregated.

The predicates are deliberately dependency-free (stdlib only) and deterministic:
"repaired" and "validated" must mean the same thing everywhere.

Two link forms are recognised, and every caller gets both for free by going through
``MD_LINK_RE`` + the parsers here: the compact ``src:<path>#L<n>`` sentinel that
generation writes (issue #54), and an absolute URL — kept parseable so a writer who
spells the base out is *validated* rather than silently skipped.
"""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from typing import Any
from urllib.parse import unquote

# A trailing `word.word` segment only means "filename" when the last part is a known
# extension; otherwise a `Class.method` citation (`RetrieverService.query`) would be
# misread as a file, since it has the same shape.
KNOWN_FILE_EXTENSIONS = {
    "ts", "tsx", "js", "jsx", "mjs", "cjs", "json", "md", "yaml", "yml",
    "py", "sh", "bash", "css", "scss", "html", "txt", "cfg", "ini", "toml",
    "lock", "env", "example", "sample", "xml", "sql", "proto", "rs", "go",
    "java", "kt", "rb", "php", "c", "h", "hpp", "cpp", "cc", "swift",
    "gradle", "csv",
}

# Conventional filenames with no extension — cited the same way `foo.ext` is
# (graded by basename, since the bare name never appears as text in its own body).
KNOWN_EXTENSIONLESS_FILENAMES = {
    "LICENSE", "README", "MAKEFILE", "DOCKERFILE", "CHANGELOG", "CONTRIBUTING",
    "AUTHORS", "NOTICE", "COPYING", "PROCFILE",
}

# Our own compact deep-link scheme (issue #54): `src:<repo-relative-path>[#L<n>]`.
# The host/owner/branch prefix is identical in every link on every page, so writing it
# out 3000+ times is pure boilerplate — ~28% of a generated wiki's characters. The
# prefix lives in `repo.json.deepLink` instead and the renderer puts it back from
# there, losslessly.
#
# A sentinel rather than a bare relative path: the pages live in `<repo>/code2spec/`,
# so `](src/x.ts)` would resolve against *that* directory and 404, and `](/src/x.ts)`
# would resolve against the site root. `src:` cannot be mistaken for either, and it
# leaves genuine relative links (page-to-page `../modules/x.md`) untouched.
SOURCE_SENTINEL = "src:"
# The anchor inside a sentinel is always `#L`, whatever the host's own anchor is
# (`#n` on cgit, `#lines-` on bitbucket): the sentinel is *our* scheme, and the host
# form is applied when it is expanded.
SENTINEL_ANCHOR = "#L"
_SENTINEL_RE = re.compile(
    rf"^{SOURCE_SENTINEL}(?P<path>[^\s#?]+)(?:{SENTINEL_ANCHOR}(?P<spec>[0-9]+(?:-L?[0-9]+)?))?$")

# Generic markdown link scanner — captures link text + URL only. Whether a URL is one
# of *our* source deep-links is decided by the parsers below, never by guessing.
# Both link forms are scanned: `src:` sentinels and absolute URLs (a writer who spells
# the base out, or a page written before #54).
MD_LINK_RE = re.compile(
    rf"\[([^\]]+?)\]\(({SOURCE_SENTINEL}[^)\s]+|https?://[^)\s]+)\)")

_PLACEHOLDER_RE = re.compile(r"[<>]")
_FILENAME_LABEL_RE = re.compile(
    r"^([A-Za-z0-9_.\-]+)\.([A-Za-z0-9]+)(?::[0-9]+(?:[-,][0-9]+)*)?$")
_FILENAME_SUBJECT_RE = re.compile(r"^([A-Za-z0-9_.\-]+)\.([A-Za-z0-9]+)$")
# The anchor may be GitHub's `#L<n>` or Gerrit gitweb's `#l<n>`.
_ANCHOR_IN_LABEL_RE = re.compile(r"#l[0-9]+", re.IGNORECASE)
_TRAILING_EXT_RE = re.compile(r"\.[a-z0-9]+$", re.IGNORECASE)
_LABEL_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
# A label token naming a source *line* rather than a code symbol: `L48`, `l7`, and each
# half of `L48-51` / `L48-L51` (the identifier regex above yields `L48` and `L51` from
# those). Such a token is a location, and grading it as a symbol contradicts a citation
# that is factually correct — the same reason `_ANCHOR_IN_LABEL_RE` already disqualifies
# a label carrying `#L123`. Anchored on the whole token, so a real identifier that merely
# starts this way (`L2_CACHE`) keeps being graded.
_LINE_REF_TOKEN_RE = re.compile(r"^[Ll][0-9]+$")
# A whole label that cites only lines: `L48`, `L48-51`, `L48-L51`, `L52, L593, L231`,
# and the bare-number forms. Tested against the label rather than its tokens because
# `_LABEL_IDENT_RE` has a 3-character floor, so a short reference (`L4-5`) yields no
# tokens at all and a token-based test would silently miss it.
_LINE_REF_LABEL_RE = re.compile(r"^[Ll]?[0-9]+(?:\s*[-,–]\s*[Ll]?[0-9]+)*$")
_BACKTICK_SPAN_RE = re.compile(r"`([^`]+)`")
_EMPHASIS_RE = re.compile(r"[*_]")
_EXT_RE = re.compile(r"\.(ts|tsx|js|mjs|cjs|json|md|py|sh|ya?ml|c|h|cpp|hpp)$",
                     re.IGNORECASE)
_CALLISH_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\s*\([^)]*\)")
_IDENT_TEXT_RE1 = re.compile(
    r"^[A-Za-z_@][A-Za-z0-9_@\-]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?(?:\([^)]*\))?$")
_IDENT_TEXT_RE2 = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*\([^)]*\)$")
_CALL_SIG_RE = re.compile(
    r"(?:[A-Za-z_$][A-Za-z0-9_$]*\.)?([A-Za-z_$][A-Za-z0-9_$]*)\s*\(([^)]*)\)")
# A documented *parameter name* starts lowercase (or _/$): `issue(userId, email)`.
# An uppercase or literal argument (`Foo(Bar)`, `issue(42, "a@b")`) documents a call's
# *values*, and grading it as a signature would contradict correct prose — so such a
# label is never treated as a signature. This is the stricter of the two rules the
# validators used to disagree on.
_PARAM_NAME_RE = re.compile(r"^[a-z_$][A-Za-z0-9_$]*$")
_ARGS_RE = re.compile(r"\([^)]*\)")
_CODE_IDENTS_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")


# ---------------------------------------------------------------------------
# Small text helpers
# ---------------------------------------------------------------------------

def leading_int(s: object) -> int | None:
    """Leading integer of a string, or None.

    The number has to be read as a prefix because range anchors (``#L10-L20``) are
    common in generated docs; ``int()`` would raise on them.
    """
    m = re.match(r"\s*([+-]?[0-9]+)", str(s))
    return int(m.group(1)) if m else None


def line_at_offset(text: str, offset: int) -> int:
    """1-based line number of a character offset."""
    return len(re.split(r"\r?\n", text[:offset]))


def is_placeholder_path(value: object) -> bool:
    """True for a template path such as ``src/<module>/index.ts``."""
    return _PLACEHOLDER_RE.search(str(value)) is not None


def norm_path(p: object) -> str:
    """Repo-relative path with ``/`` separators and no leading ``./``."""
    return re.sub(r"^\./", "", str(p or "").replace(os.sep, "/"), count=1)


def join_within(root: str, rel: object) -> str:
    """Join ``rel`` under ``root`` even when ``rel`` looks absolute.

    Deep-link paths and claim files are inputs, not trusted code: ``os.path.join``
    would discard ``root`` entirely for a leading ``/``, letting a crafted or buggy
    path read outside the repo. Concatenating first keeps every lookup under ``root``.
    """
    return os.path.normpath(root + os.sep + str(rel))


# ---------------------------------------------------------------------------
# URL → (file, line) parsers
# ---------------------------------------------------------------------------

def parse_sentinel(url: str) -> dict[str, Any] | None:
    """Parse a ``src:<path>[#L<n>]`` link into ``{kind, file, line, anchor, url}``.

    Needs no repo.json: the sentinel carries the repo-relative path itself, so a
    citation stays checkable even when the deep-link base could not be resolved.
    ``line`` is None for a whole-file sentinel.
    """
    m = _SENTINEL_RE.match(url)
    if not m:
        return None
    path = m.group("path")
    if is_placeholder_path(path):
        return None
    spec = m.group("spec")
    return {"kind": "sentinel", "file": path, "line": leading_int(spec) if spec else None,
            "anchor": SENTINEL_ANCHOR, "url": url}


def make_source_url_parser(
    deep_link: Any,
) -> Callable[[str], dict[str, Any] | None]:
    """Build a ``url → {kind, file, line, anchor, url}`` parser for this deep-link config.

    Handles both link forms: a ``src:`` sentinel (config-independent) and an absolute
    URL. For the latter it uses the exact ``base``/``type``/``lineAnchorPrefix``
    recorded in repo.json rather than a generic regex, because guessing where the
    branch segment ends breaks as soon as the branch name itself contains a ``/``
    (``test/incremental-pipeline``).

    Only line-anchored citations are returned; a whole-file link is
    :func:`make_file_only_parser`'s job. An absolute URL matches nothing when repo.json
    carries no usable config, so it is reported as uncheckable rather than mis-parsed —
    sentinels still parse. The path is percent-decoded (except gerrit gitweb, whose
    ``f=`` value is read verbatim) and a template placeholder path (``src/<module>/…``)
    matches nothing. ``line == 0`` is accepted so it can be *reported* as out-of-range
    instead of silently dropped.
    """
    parse_absolute = _make_absolute_url_parser(deep_link)

    def parse(url: str) -> dict[str, Any] | None:
        if url.startswith(SOURCE_SENTINEL):
            parsed = parse_sentinel(url)
            return parsed if parsed and parsed["line"] is not None else None
        return parse_absolute(url)

    return parse


def _make_absolute_url_parser(
    deep_link: Any,
) -> Callable[[str], dict[str, Any] | None]:
    """The absolute-URL half of :func:`make_source_url_parser`."""
    if not isinstance(deep_link, dict) or not deep_link.get("base") \
            or not deep_link.get("lineAnchorPrefix"):
        return lambda url: None
    type_ = deep_link.get("type")
    base = deep_link["base"]
    prefix = deep_link["lineAnchorPrefix"]

    def parse(url: str) -> dict[str, Any] | None:
        if type_ == "gerrit-gitweb":
            # base already ends in `f=`; the path is followed by `;`-separated params.
            # The path stays percent-encoded here: gitweb's `f=` value is read verbatim.
            if not url.startswith(base):
                return None
            rest = url[len(base):]
            kind, cut, decode = "gerrit-gitweb", ";", False
        elif type_ == "cgit":
            # base + '/' + path + '?h=<branch>' + anchor
            if not url.startswith(f"{base}/"):
                return None
            rest = url[len(base) + 1:]
            kind, cut, decode = "cgit-tree", "?", True
        else:
            # github / gitlab / bitbucket / github-fallback
            if not url.startswith(f"{base}/"):
                return None
            rest = url[len(base) + 1:]
            kind, cut, decode = "github-blob", "", True
        anchor_idx = rest.rfind(prefix)
        if anchor_idx == -1:
            return None
        file = rest[:anchor_idx]
        if cut:
            idx = file.find(cut)
            if idx != -1:
                file = file[:idx]
        if decode:
            file = unquote(file)
        if not file or is_placeholder_path(file):
            return None
        line = leading_int(rest[anchor_idx + len(prefix):])
        if line is None:
            return None
        return {"kind": kind, "file": file, "line": line, "anchor": prefix, "url": url}

    return parse


def make_file_only_parser(
    deep_link: Any,
) -> Callable[[str], dict[str, Any] | None]:
    """Parser for a whole-file link with no line anchor, e.g. an RSF block's
    ``[src/foo.ts](src:src/foo.ts)``. Returns ``{kind, file, line: None, url}``.

    For absolute URLs only the github-shaped hosts are handled: a cgit or gerrit URL
    carries query parameters that make a file-only form ambiguous, so those are left to
    the line-anchored parser. A ``src:`` sentinel has no such ambiguity and is always
    parsed.
    """
    parse_absolute = _make_absolute_file_only_parser(deep_link)

    def parse(url: str) -> dict[str, Any] | None:
        if url.startswith(SOURCE_SENTINEL):
            parsed = parse_sentinel(url)
            return {**parsed, "kind": "file-only"} \
                if parsed and parsed["line"] is None else None
        return parse_absolute(url)

    return parse


def _make_absolute_file_only_parser(
    deep_link: Any,
) -> Callable[[str], dict[str, Any] | None]:
    """The absolute-URL half of :func:`make_file_only_parser`."""
    if not isinstance(deep_link, dict) or not deep_link.get("base"):
        return lambda url: None
    type_ = deep_link.get("type")
    base = deep_link["base"]
    suffix = deep_link.get("suffix")
    if type_ == "cgit" or type_ == "gerrit-gitweb":
        return lambda url: None

    def parse(url: str) -> dict[str, Any] | None:
        if not url.startswith(f"{base}/"):
            return None
        rest = url[len(base) + 1:]
        if "#" in rest:
            return None                # has a line anchor → the other parser's job
        if suffix and rest.endswith(suffix):
            rest = rest[:len(rest) - len(suffix)]
        if not rest or "?" in rest:
            return None
        rest = unquote(rest)
        if is_placeholder_path(rest):
            return None
        return {"kind": "file-only", "file": rest, "line": None, "url": url}

    return parse


# ---------------------------------------------------------------------------
# Label classification
# ---------------------------------------------------------------------------

def extract_filename_label(link_text: str, require_backtick: bool = True) -> str | None:
    """The filename a label cites (``foo.cjs``, ``foo.cjs:18``, ``foo.ts:39-45``).

    Manifest and config rows have no symbol to cite, so they cite the file itself.
    Such a citation is graded by comparing the label against the linked file's
    basename — a filename never appears as text inside its own source lines.

    ``require_backtick`` mirrors the grounding gate's contract (only a backticked
    label is a code citation); harvesters that also want plain filename labels pass
    False.
    """
    if require_backtick and "`" not in link_text:
        return None
    cleaned = link_text.replace("`", "").strip()
    if "/" in cleaned:
        return None
    # Extension-less conventional filenames (LICENSE, README, Makefile, ...) cite
    # themselves the same way `foo.ext` does — no dot to split, so _FILENAME_LABEL_RE
    # never matches them; check the bare name against the well-known set instead.
    bare = cleaned.split(":", 1)[0]
    if bare.upper() in KNOWN_EXTENSIONLESS_FILENAMES:
        return bare
    m = _FILENAME_LABEL_RE.match(cleaned)
    if not m:
        return None
    base, ext = m.group(1), m.group(2)
    if ext.lower() not in KNOWN_FILE_EXTENSIONS:
        return None
    return f"{base}.{ext}"


def filename_subject(id_: object) -> str | None:
    """The filename a claim subject names, or None when it is a code symbol.

    A subject like ``chunk.ts`` is a *file reference*, while ``Service.query`` is a
    symbol; both have the same ``word.word`` shape, so the extension decides.
    """
    m = _FILENAME_SUBJECT_RE.match(str(id_))
    if not m:
        return None
    return f"{m.group(1)}.{m.group(2)}" \
        if m.group(2).lower() in KNOWN_FILE_EXTENSIONS else None


def is_line_ref_token(token: object) -> bool:
    """True when a label token names a source line (``L48``) rather than a symbol."""
    return _LINE_REF_TOKEN_RE.match(str(token)) is not None


def is_line_reference_label(link_text: str) -> bool:
    """True when a label cites only source lines: `` `L48-51` ``, `` `L52`, `L593` ``.

    Such a label is not a broken symbol citation but a deliberate *location* citation,
    so a repair tool must leave it alone rather than overwrite it with whatever symbol
    happens to sit on the cited line.

    Backticks are *not* required here, unlike the code-citation predicates: `[L48-51]`
    states the same thing as `` [`L48-51`] `` and is equally not a symbol. Callers that
    do require the backtick signal (``extract_symbol``) have already checked for it.
    """
    cleaned = link_text.replace("`", "").strip()
    if "/" in cleaned:
        return False
    return _LINE_REF_LABEL_RE.match(cleaned) is not None


def extract_label_identifiers(link_text: str) -> list[str]:
    """Code identifiers a label cites, or an empty list when it cites no symbol.

    Only a backticked label counts as a code citation, and a path-shaped one (holding
    ``/``, a line anchor or a file extension) is a path reference rather than a symbol.
    Every identifier of 3+ characters is returned so compound labels
    (``Class::method``, ``var = value``) can be graded by "does *any* of them appear".

    Tokens naming a source line are dropped: `` `L48-51` `` asserts a location, not that
    the text ``L48`` appears on line 48, so grading it as an identifier turns a correct
    citation into a drift.
    """
    if "`" not in link_text:
        return []
    cleaned = link_text.replace("`", "").strip()
    if "/" in cleaned:
        return []
    if _ANCHOR_IN_LABEL_RE.search(cleaned):
        return []
    if _TRAILING_EXT_RE.search(cleaned):
        return []
    return [i for i in _LABEL_IDENT_RE.findall(cleaned) if not is_line_ref_token(i)]


def extract_symbol(link_text: str) -> str | None:
    """The symbol a backticked label cites; backticks are required as the code-citation
    signal, and a path-shaped, filename-shaped or line-shaped label is not a symbol."""
    if "`" not in link_text:
        return None
    cleaned = link_text.replace("`", "").strip()
    if "/" in cleaned:
        return None
    if _ANCHOR_IN_LABEL_RE.search(cleaned):
        return None
    if _TRAILING_EXT_RE.search(cleaned) and "(" not in cleaned:
        return None                    # a filename, unless it is a signature
    if is_line_reference_label(link_text):
        return None                    # cites a line, not a symbol
    return cleaned or None


def is_code_identifier_text(value: str) -> bool:
    """True when a label looks like a code symbol rather than a path or prose."""
    text = str(value).strip()
    if not text:
        return False
    if "/" in text:
        return False
    if _ANCHOR_IN_LABEL_RE.search(text):
        return False
    if _EXT_RE.search(text):
        return False
    if re.search(r"\s", text) and not _CALLISH_RE.search(text):
        return False
    return bool(_IDENT_TEXT_RE1.match(text)) or bool(_IDENT_TEXT_RE2.match(text))


def code_like_text(markdown_text: str) -> str:
    """The code-symbol part of a link label, or "" when it cites no symbol.

    Backticked spans are preferred; a label with no backticks is accepted only when
    the whole label is itself a symbol.
    """
    code = " ".join(v for v in _BACKTICK_SPAN_RE.findall(markdown_text)
                    if is_code_identifier_text(v)).strip()
    if code:
        return code
    trimmed = _EMPHASIS_RE.sub("", markdown_text).strip()
    return trimmed if is_code_identifier_text(trimmed) else ""


def extract_code_identifiers(text: str) -> list[str]:
    """Distinct 3+ character identifiers in a label, ignoring argument lists.

    Line-reference tokens are excluded for the same reason URL words are: ``L48`` names
    a location, so requiring it to appear in the linked file contradicts a correct
    citation (see ``extract_label_identifiers``).
    """
    without_args = _ARGS_RE.sub(" ", text)
    ids = _CODE_IDENTS_RE.findall(without_args)
    return list(dict.fromkeys(
        [i for i in ids
         if i not in ("http", "https", "blob", "main") and not is_line_ref_token(i)]))


# ---------------------------------------------------------------------------
# Identifier matching
# ---------------------------------------------------------------------------

def word_re(ident: object) -> re.Pattern[str]:
    """``ident`` as a whole identifier, treating ``$`` as part of an identifier.

    ``\\b`` is wrong here: it sees ``$`` as a boundary, so ``\\bfoo\\b`` would match
    inside ``$foo``. This boundary is also what makes ``Store`` *not* match inside
    ``StoreFactory`` — a citation must name the symbol on the line, not a prefix of a
    different one.
    """
    return re.compile(
        rf"(?<![A-Za-z0-9_$]){re.escape(str(ident))}(?![A-Za-z0-9_$])")


def has_identifier(text: str, id_: object) -> bool:
    """True when ``id_`` occurs in ``text`` as a whole identifier."""
    return word_re(id_).search(text) is not None


def identifier_on_line(lines: list[str], line_no: int, identifiers: list[str]) -> bool:
    """True when any cited identifier appears on the 1-based ``line_no``."""
    if line_no < 1 or line_no > len(lines):
        return False
    line = lines[line_no - 1]
    return any(has_identifier(line, i) for i in identifiers)


def line_in_range(lines: list[str], line_no: int) -> bool:
    """True when the 1-based ``line_no`` exists in the file."""
    return 1 <= line_no <= len(lines)


def basename_matches(rel_file: object, filename_label: str) -> bool:
    """True when a filename label names the linked file's basename."""
    return os.path.basename(norm_path(rel_file)) == filename_label


# ---------------------------------------------------------------------------
# Call signatures
# ---------------------------------------------------------------------------

def norm_param(param: object) -> str:
    """One parameter name, stripped of its default, type annotation and modifiers."""
    s = str(param).strip()
    if not s:
        return ""
    s = s.split("=")[0]      # default value
    s = s.split(":")[0]      # type annotation
    s = re.sub(r"\?$", "", re.sub(r"^\.\.\.", "", s.strip())).strip()
    words = re.split(r"\s+", s)     # "public foo" → the last token
    return words[-1].replace("?", "")


def parse_call_signature(text: object) -> dict[str, Any] | None:
    """``{method, params}`` for a call-shaped label, or None.

    None is returned when:

    * the argument list is empty. In prose ``fn()`` is the conventional way to write
      "the function ``fn``", not an assertion that it takes no arguments — reading it
      as a zero-parameter signature contradicts every citation whose author simply
      omitted the arguments. The method *name* is still graded, by the identifier and
      symbol-existence checks;
    * any argument is not a plain lowercase-start parameter name, so a label
      documenting *values* (``issue(42, "a@b")``, ``Foo(Bar)``) is never graded as a
      signature (see ``_PARAM_NAME_RE``).
    """
    match = _CALL_SIG_RE.search(str(text))
    if not match:
        return None
    raw = match.group(2)
    if not raw.strip():
        return None
    params = [p for p in (norm_param(x) for x in split_params(raw)) if p]
    if not all(_PARAM_NAME_RE.match(p) for p in params):
        return None
    return {"method": match.group(1), "params": params}


def find_method(text: str, method_name: str,
                near_line: int | None = None) -> dict[str, Any] | None:
    """Locate a function/arrow/method declaration and return its signature + line.

    Several same-named declarations can exist in one file; when ``near_line`` (the
    cited ``#L``) is given, the declaration closest to it wins, so a signature is
    graded against the declaration the citation actually points at. Without it, the
    highest-priority pattern's first match is kept (function > const > method).
    """
    name = re.escape(method_name)
    patterns = [
        re.compile(rf"^\s*(?:export\s+)?(?:async\s+)?function\s+{name}\s*"
                   rf"\(([^)]*)\)\s*(?::[^\n{{;]+)?\s*\{{", re.M),
        re.compile(rf"^\s*(?:export\s+)?const\s+{name}\s*=\s*(?:async\s*)?"
                   rf"\(([^)]*)\)\s*(?::[^\n=]+)?=>", re.M),
        re.compile(rf"^\s*(?:(?:public|private|protected|static|async|abstract|override)"
                   rf"\s+)*{name}\s*\(([^)]*)\)\s*(?::[^\n{{;]+)?\s*(?:\{{|;)", re.M),
    ]
    candidates: list[tuple[int, int, dict[str, Any]]] = []
    for priority, r in enumerate(patterns):
        for match in r.finditer(text):
            sig = re.sub(r"[;{]\s*$", "", match.group(0), count=1)
            sig = re.sub(r"=>\s*$", "", sig, count=1).strip()
            candidates.append((priority, line_at_offset(text, match.start()),
                               {"signature": sig,
                                "line": line_at_offset(text, match.start())}))
    if not candidates:
        return None
    if near_line is not None:
        return min(candidates, key=lambda c: (abs(c[1] - near_line), c[0]))[2]
    return min(candidates, key=lambda c: (c[0], c[1]))[2]


def split_params(raw: str) -> list[str]:
    """Split a parameter list on the commas that actually separate parameters.

    A type argument (``Record<string, unknown>``), an inline object type
    (``{a: string, b: number}``) or a nested call all contain commas that separate
    nothing. Splitting on every comma invents a parameter — ``Record<string, unknown>``
    yields a phantom ``unknown>`` — and the invented name then contradicts even a
    correctly documented signature, so bracket depth is tracked.

    ``=>`` and ``->`` are arrows, not closing brackets. A bare ``<`` used as less-than
    inside a default value would still be read as an opener; that shape does not occur
    in the declarations ``find_method`` matches.
    """
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    prev = ""
    for ch in raw:
        if ch in "<([{":
            depth += 1
        elif ch in ">)]}" and not (ch == ">" and prev in "=-"):
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        prev = ch
    parts.append("".join(buf))
    return parts


def _closing_paren(text: str, start: int) -> int:
    """Index of the ``)`` closing the ``(`` at ``start``, or -1.

    The first ``)`` is not necessarily the right one: a callback parameter
    (``run(cb: (x) => void, times: number)``) closes an inner list first, and cutting
    there drops every parameter after it.
    """
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1


def parse_parameters(signature: str) -> list[str]:
    """Parameter names of a declaration, stripped of types, defaults and modifiers."""
    start = signature.find("(")
    end = _closing_paren(signature, start) if start >= 0 else -1
    if start < 0 or end < 0:
        return []
    raw = signature[start + 1:end].strip()
    if not raw:
        return []
    return [p for p in (norm_param(x) for x in split_params(raw)) if p]


# ---------------------------------------------------------------------------
# Source access
# ---------------------------------------------------------------------------

class SourceReader:
    """Cached, root-confined reads of cited source files.

    A wiki cites the same file many times, so each file is read at most once. Every
    lookup goes through :func:`join_within`, so a crafted deep-link path cannot
    escape the repo root.
    """

    def __init__(self, repo_root: str) -> None:
        self.repo_root = repo_root
        self._cache: dict[str, dict[str, Any] | None] = {}

    def path(self, rel: object) -> str:
        return join_within(self.repo_root, rel)

    def read(self, rel: object) -> dict[str, Any] | None:
        """``{text, lines}`` of a repo-relative file, or None when unreadable."""
        abs_ = self.path(rel)
        if abs_ not in self._cache:
            try:
                with open(abs_, encoding="utf-8", errors="replace") as f:
                    text = f.read()
                self._cache[abs_] = {"text": text, "lines": re.split(r"\r?\n", text)}
            except OSError:
                self._cache[abs_] = None
        return self._cache[abs_]
