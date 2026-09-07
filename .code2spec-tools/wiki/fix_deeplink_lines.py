#!/usr/bin/env python3
"""Correct deep-link `#L` line numbers against `.ast/api.json`, and collapse
duplicated owner segments in deep-link URLs.

A writer who guesses a symbol's line often lands on an import instead of the
definition, which shows up as grounding drift. The correct answer is unambiguous —
it is the definition line recorded in api.json — so finalize applies it here rather
than leaving it to an ad-hoc script.

Safety rules that keep this from making things worse:

* Only a **backticked symbol** is corrected, and only to a line where that identifier
  demonstrably lives. api.json exports come first; when the symbol is not exported
  (an internal helper or constant, which api.json does not record) the linked file
  itself is scanned and a **definition-like** line for that identifier is used.
* An identifier that appears **nowhere in the linked file** is left alone — that is a
  wrong symbol name, a real error, and claimGrounding must report it rather than have
  it remapped out of sight. The same holds when the file only *uses* the identifier
  (imports, call sites) with no definition: there is no unambiguous definition line to
  move to, so the citation stays as written and the grounding gate reports it.
* ``Class.member`` resolves to the **member**, never to its container. If the member
  is missing from api.json the citation stays as written; silently pointing at the
  class line would turn a precise citation into a wrong one.
* Owner de-duplication only collapses ``<owner>/<owner>/`` — the owner is taken from
  the configured base, so no other path segment can be affected.

Usage: python3 fix_deeplink_lines.py --wiki-dir <dir> [--repo-json <path>]
                                     [--repo-root <dir>]
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any

# The shared predicate module is the single source of truth for URL parsing and
# identifier matching — the same functions the validators call (issue #33).
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "verification"))

from citation_checks import (  # noqa: E402
    KNOWN_FILE_EXTENSIONS,
    MD_LINK_RE,
    make_source_url_parser,
    word_re,
)

_ANCHOR_IN_LABEL_RE = re.compile(r"#l[0-9]+", re.IGNORECASE)
_FILENAME_RE = re.compile(r"^[A-Za-z0-9_.\-]+\.([A-Za-z0-9]+)\Z")
_CALL_RE = re.compile(r"^([A-Za-z_$][A-Za-z0-9_$.]*)\s*\(")
_IDENT_RE = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*")
_OWNER_RE = re.compile(r"^https?://[^/]+/([^/]+)/")

SKIP_DIRS = {".ast", ".claims", ".trust", ".git", ".analysis", "node_modules"}

# Lines that merely pull a name in from elsewhere are never the definition.
_IMPORT_LINE_RE = re.compile(
    r"^\s*(?:import\b|from\b|export\s+\{|#include\b|using\b|use\b|require\s*\()")
# Declaration keywords across the languages code2spec analyses. A line carrying one of
# these *and* the identifier is treated as the definition.
_DECL_KEYWORDS = (
    "class", "interface", "enum", "struct", "trait", "type", "def", "function",
    "fn", "func", "const", "let", "var", "val", "public", "private", "protected",
    "static", "async", "export", "abstract", "final", "record", "module",
)
_DECL_KEYWORD_RE = re.compile(r"\b(?:" + "|".join(_DECL_KEYWORDS) + r")\b")


def walk(dir_: str) -> list[str]:
    """Every ``.md`` file under ``dir_``, skipping generated trees and symlinks."""
    out: list[str] = []
    for ent in sorted(os.scandir(dir_), key=lambda e: e.name):
        fp = os.path.join(dir_, ent.name)
        if ent.is_dir(follow_symlinks=False):
            if ent.name not in SKIP_DIRS:
                out.extend(walk(fp))
        elif ent.name.endswith(".md"):
            out.append(fp)
    return out


def norm_path(p: object) -> str:
    """Repo-relative path with ``/`` separators and no leading ``./``."""
    return re.sub(r"^\./", "", str(p or "").replace(os.sep, "/"))


def read_json(p: str) -> Any | None:
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return json.loads(f.read())
    except (OSError, ValueError):
        return None


def build_file_symbols(api: Any) -> dict[str, dict[str, int]]:
    """``{repo-relative file: {symbol: definition line}}`` from api.json."""
    file_syms: dict[str, dict[str, int]] = {}
    for f in ((api.get("files") if isinstance(api, dict) else None) or []):
        syms: dict[str, int] = {}
        for e in (f.get("exports") or []):
            if e.get("name") and e.get("line"):
                syms[e["name"]] = e["line"]
        file_syms[norm_path(f.get("path"))] = syms
    return file_syms


def resolve_symbol_line(link_text: str, syms: dict[str, int]) -> int | None:
    """Definition line for a backticked symbol label, or None to leave the link alone.

    ``Class.member`` is tried as the full name first and then as the member; the
    container is never used as a fallback (see the module docstring).
    """
    if "`" not in link_text:
        return None
    s = link_text.replace("`", "").strip()
    if not s or "/" in s or _ANCHOR_IN_LABEL_RE.search(s):
        return None
    fnm = _FILENAME_RE.match(s)
    if fnm and fnm.group(1).lower() in KNOWN_FILE_EXTENSIONS:
        return None                                  # a filename, not a symbol
    call = _CALL_RE.match(s)
    if call:
        s = call.group(1)                            # `name(args)` → `name`
    if "." in s:
        candidates = [s, s.split(".")[-1]]
    else:
        m = _IDENT_RE.match(s)
        candidates = [m.group(0)] if m else []
    for c in candidates:
        if c in syms:
            return syms[c]
    return None


def label_identifier(link_text: str) -> str | None:
    """The bare identifier a backticked symbol label cites, or None.

    Shares the gating of :func:`resolve_symbol_line` — filenames, paths and labels
    holding a line anchor are not symbol citations.
    """
    if "`" not in link_text:
        return None
    s = link_text.replace("`", "").strip()
    if not s or "/" in s or _ANCHOR_IN_LABEL_RE.search(s):
        return None
    fnm = _FILENAME_RE.match(s)
    if fnm and fnm.group(1).lower() in KNOWN_FILE_EXTENSIONS:
        return None
    call = _CALL_RE.match(s)
    if call:
        s = call.group(1)
    if "." in s:
        s = s.split(".")[-1]                         # `Class.member` → `member`
    m = _IDENT_RE.match(s)
    return m.group(0) if m else None


def resolve_by_source_scan(ident: str, lines: list[str]) -> int | None:
    """1-based line where ``ident`` is *defined* in ``lines``, or None.

    Only declaration-looking lines qualify. A file that merely imports or calls the
    identifier gives no unambiguous definition line, so None is returned and the
    citation is left for the grounding gate to report — moving it to a call site
    would trade a detectable error for a plausible-looking wrong one.
    """
    wr = word_re(ident)
    best: tuple[int, int] | None = None            # (score, line)
    for i, line in enumerate(lines, start=1):
        if not wr.search(line):
            continue
        if _IMPORT_LINE_RE.match(line):
            continue
        score = 0
        head = line[:wr.search(line).start()]
        if _DECL_KEYWORD_RE.search(head):
            score += 3
        if re.search(rf"{wr.pattern}\s*[=:(]", line):
            score += 2
        if score > 0 and (best is None or score > best[0]):
            best = (score, i)
    return best[1] if best else None


def main() -> int:
    argv = sys.argv[1:]

    def arg(name: str) -> str | None:
        try:
            i = argv.index(name)
        except ValueError:
            return None
        return argv[i + 1] if i + 1 < len(argv) else None

    wiki_dir = os.path.abspath(arg("--wiki-dir") or ".")
    repo_json_path = arg("--repo-json") or os.path.join(wiki_dir, "repo.json")
    repo_root = os.path.abspath(arg("--repo-root") or ".")

    repo_json = read_json(repo_json_path)
    deep_link = repo_json.get("deepLink") if isinstance(repo_json, dict) else None
    deep_link = deep_link if isinstance(deep_link, dict) else {}
    base = deep_link.get("base")
    if not base or not deep_link.get("lineAnchorPrefix"):
        # `src:` sentinels carry their own path and anchor, so they are still repairable
        # without a resolved base — only full-URL links become unparseable.
        print("[fix-deeplink-lines] repo.json deepLink(base/lineAnchorPrefix) 없음 "
              "— src: 축약 링크만 교정")

    file_syms = build_file_symbols(
        read_json(os.path.join(wiki_dir, ".ast", "api.json")) or {"files": []})
    parse_source_url = make_source_url_parser(deep_link)

    # A writer who pastes the owner twice produces `/<owner>/<owner>/`; the owner comes
    # from the configured base so nothing else can match.
    owner_dup: str | None = None
    owner_fix: str | None = None
    owner_match = _OWNER_RE.match(str(base)) if base else None
    if owner_match:
        owner = owner_match.group(1)
        owner_dup = f"/{owner}/{owner}/"
        owner_fix = f"/{owner}/"

    # Source files are read at most once each; a wiki cites the same file many times.
    source_cache: dict[str, list[str] | None] = {}

    def source_lines(rel_path: str) -> list[str] | None:
        if rel_path not in source_cache:
            try:
                with open(os.path.join(repo_root, rel_path),
                          encoding="utf-8", errors="replace") as f:
                    source_cache[rel_path] = f.read().split("\n")
            except OSError:
                source_cache[rel_path] = None
        return source_cache[rel_path]

    line_fixes = 0
    scan_fixes = 0
    owner_fixes = 0
    files_changed = 0
    for md in walk(wiki_dir):
        with open(md, encoding="utf-8", errors="replace") as f:
            text = f.read()
        before = text

        if owner_dup and owner_fix and owner_dup in text:
            owner_fixes += text.count(owner_dup)
            text = text.replace(owner_dup, owner_fix)

        fixed_here = 0

        def fix_line(mo: re.Match[str]) -> str:
            nonlocal fixed_here, scan_fixes
            label, url = mo.group(1), mo.group(2)
            parsed = parse_source_url(url)
            if not parsed:
                return mo.group(0)
            rel = norm_path(parsed["file"])
            syms = file_syms.get(rel)
            correct = resolve_symbol_line(label, syms) if syms is not None else None

            # api.json only records exports, so an internal helper or constant needs
            # the file itself. Only run the scan when the cited line is actually wrong.
            from_scan = False
            if correct is None:
                ident = label_identifier(label)
                lines = source_lines(rel) if ident else None
                if ident and lines is not None:
                    cited = lines[parsed["line"] - 1] \
                        if 1 <= parsed["line"] <= len(lines) else ""
                    if not word_re(ident).search(cited):
                        correct = resolve_by_source_scan(ident, lines)
                        from_scan = correct is not None

            if correct is not None and correct != parsed["line"]:
                # The parser reports which anchor this link actually uses — the host's
                # (`#L`·`#n`·`#l`) for a full URL, `#L` for a `src:` sentinel — so the
                # rewrite cannot substitute the wrong one.
                anchor = parsed["anchor"]
                anchor_idx = url.rfind(anchor)
                new_url = url[:anchor_idx] + anchor + str(correct)
                fixed_here += 1
                if from_scan:
                    scan_fixes += 1
                return f"[{label}]({new_url})"
            return mo.group(0)

        text = MD_LINK_RE.sub(fix_line, text)
        line_fixes += fixed_here

        if text != before:
            with open(md, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            files_changed += 1

    print(f"[fix-deeplink-lines] line-fixes={line_fixes} (from-api-json="
          f"{line_fixes - scan_fixes} from-source-scan={scan_fixes}) "
          f"owner-dedup={owner_fixes} files-changed={files_changed}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
