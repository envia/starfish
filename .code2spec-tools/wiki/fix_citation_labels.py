#!/usr/bin/env python3
"""Rewrite source deep-link labels that grounding cannot check into ones it can.

`grounding` only grades a citation whose label is a **backticked code reference** —
either a symbol (`` [`RetrieverService`](…#L42) ``) or a filename
(`` [`package.json`](…#L12) ``). A label like ``[출처](…#L42)`` or a backticked but
path-shaped one (`` [`src/foo.ts`](…#L42) ``) is neither, so the validator counts it
as *skipped*: it is excluded from the score's denominator and can never fail the hard
gate. A wrong line hidden behind such a label therefore survives forever.

The writing rules forbid producing those labels in the first place (see
``agent/skills/code2spec-doc-generation/references/grounding-and-deep-links.md`` §3).
This step is the deterministic safety net for whatever slips through, in the same
spirit as ``convert_source_tags`` and ``quote_mermaid_labels``.

The checkability predicates are **imported from the validator** rather than
re-implemented, so the repair and the gate can never disagree about what counts as a
checkable label.

Repair order for an uncheckable label, given the cited ``<file>#L<n>``:

1. The symbol that api.json records as **defined on line n** of that file → use its
   name. The citation becomes a precise symbol reference.
2. Otherwise the linked file's **basename** (when its extension is one the validator
   knows) → the citation becomes a file-scope reference, graded by basename match.
   Nothing deterministic can recover which symbol was meant when no definition starts
   on the cited line, so the claim is narrowed to one that is true and checkable
   rather than guessed.
3. Otherwise the link is left exactly as written — a label this step cannot make
   checkable is left for a human to fix rather than papered over.

Only the link *label* changes; URLs are never touched (``fix_deeplink_lines`` owns
line numbers). Links with no line anchor — the ``Relevant source files`` block — are
skipped, so the wikiStructure block's plain path labels are preserved.

Usage: python3 fix_citation_labels.py --wiki-dir <dir> [--repo-json <path>]
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any

# The shared predicate module is the single source of truth for "can grounding check
# this label?" — the same functions the validators call (issue #33).
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "verification"))

from citation_checks import (  # noqa: E402
    KNOWN_FILE_EXTENSIONS,
    MD_LINK_RE,
    extract_filename_label,
    extract_label_identifiers,
    is_line_reference_label,
    make_source_url_parser,
)

SKIP_DIRS = {".ast", ".claims", ".trust", ".git", ".analysis", "node_modules"}


def walk(dir_: str) -> list[str]:
    """Every ``.md`` file under ``dir_``, skipping generated trees and symlinks."""
    out: list[str] = []
    try:
        entries = sorted(os.scandir(dir_), key=lambda e: e.name)
    except OSError:
        return out
    for ent in entries:
        fp = os.path.join(dir_, ent.name)
        if ent.is_dir(follow_symlinks=False):
            if ent.name not in SKIP_DIRS:
                out.extend(walk(fp))
        elif ent.is_file(follow_symlinks=False) and ent.name.endswith(".md"):
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


def build_line_symbols(api: Any) -> dict[str, dict[int, str]]:
    """``{repo-relative file: {definition line: symbol name}}`` from api.json.

    The first export recorded for a line wins; several names can share one line
    (``export { a, b }``) and any of them makes the citation checkable.
    """
    out: dict[str, dict[int, str]] = {}
    for f in ((api.get("files") if isinstance(api, dict) else None) or []):
        by_line: dict[int, str] = {}
        for e in (f.get("exports") or []):
            name, line = e.get("name"), e.get("line")
            if name and line and line not in by_line:
                by_line[int(line)] = str(name)
        out[norm_path(f.get("path"))] = by_line
    return out


def is_checkable(label: str) -> bool:
    """Whether ``grounding`` would grade a citation carrying this label."""
    return bool(extract_filename_label(label)) \
        or len(extract_label_identifiers(label)) > 0


def repair_label(label: str, file_path: str, line_no: int,
                 line_symbols: dict[str, dict[int, str]]) -> str | None:
    """A checkable replacement for ``label``, or None to leave the link alone."""
    symbol = line_symbols.get(norm_path(file_path), {}).get(line_no)
    if symbol:
        candidate = f"`{symbol}`"
        # A 1-2 character symbol yields no identifier for the validator's 3+ char
        # rule, so it would stay uncheckable — fall through to the filename.
        if is_checkable(candidate):
            return candidate

    basename = os.path.basename(norm_path(file_path))
    ext = basename.rsplit(".", 1)[-1].lower() if "." in basename else ""
    if ext in KNOWN_FILE_EXTENSIONS:
        candidate = f"`{basename}`"
        if is_checkable(candidate):
            return candidate
    return None


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

    repo_json = read_json(repo_json_path)
    deep_link = repo_json.get("deepLink") if isinstance(repo_json, dict) else None
    deep_link = deep_link if isinstance(deep_link, dict) else {}
    if not deep_link.get("base") or not deep_link.get("lineAnchorPrefix"):
        # `src:` sentinels are parseable without a base, so only full-URL citations go
        # unrepaired here — and grounding grades exactly the same set.
        print("[fix-citation-labels] repo.json deepLink(base/lineAnchorPrefix) 없음 "
              "— src: 축약 링크만 교정")

    parse_source_url = make_source_url_parser(deep_link)
    line_symbols = build_line_symbols(
        read_json(os.path.join(wiki_dir, ".ast", "api.json")) or {"files": []})

    to_symbol = 0
    to_filename = 0
    unrepairable: list[str] = []
    files_changed = 0

    for md in walk(wiki_dir):
        with open(md, encoding="utf-8", errors="replace") as f:
            text = f.read()
        before = text

        # `page` is bound per iteration on purpose: the closure runs synchronously
        # inside this iteration's `sub`, but binding it keeps that explicit.
        def relabel(mo: re.Match[str], page: str = md) -> str:
            nonlocal to_symbol, to_filename
            label, url = mo.group(1), mo.group(2)
            parsed = parse_source_url(url)
            if not parsed:
                return mo.group(0)          # not a line-anchored source deep-link
            if is_checkable(label):
                return mo.group(0)          # already graded by grounding
            if is_line_reference_label(label):
                # `` `L48-51` `` is not an unchecked symbol citation waiting to be
                # repaired — it deliberately cites a location, which grounding sets
                # aside by design. Rewriting it to whatever symbol sits on that line
                # would replace the author's accurate reference with a different claim,
                # and would do so again on every finalize run.
                return mo.group(0)
            new_label = repair_label(
                label, parsed["file"], parsed["line"], line_symbols)
            if new_label is None:
                unrepairable.append(
                    f"{os.path.relpath(page, wiki_dir)}: [{label}] → "
                    f"{parsed['file']}#L{parsed['line']}")
                return mo.group(0)
            if new_label.strip("`") == os.path.basename(norm_path(parsed["file"])):
                to_filename += 1
            else:
                to_symbol += 1
            return f"[{new_label}]({url})"

        text = MD_LINK_RE.sub(relabel, text)

        if text != before:
            with open(md, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            files_changed += 1

    print(f"[fix-citation-labels] to-symbol={to_symbol} to-filename={to_filename} "
          f"unrepairable={len(unrepairable)} files-changed={files_changed}")
    # Listed explicitly: these stay invisible to grounding, so they need a human.
    for u in unrepairable[:20]:
        print(f"  - {u}")
    if len(unrepairable) > 20:
        print(f"  … {len(unrepairable) - 20} more")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
