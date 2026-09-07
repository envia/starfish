#!/usr/bin/env python3
"""Turn code2spec's `[Source: path:L#]` citations into clickable deep-links.

A `[Source: …]` tag renders as plain text and is invisible to grounding validation, so
any left in the generated docs is frozen here into a `` [`path`](src:path#L42) ``
deep-link — the compact sentinel form the renderer expands with
``repo.json.deepLink.base`` (issue #54).

This is a safety net for finalize: when the generation step already emitted
deep-links there is nothing to convert and the run is a no-op.

Conversion still requires a resolved ``deepLink.base``. The sentinel itself does not
need one, but an unresolved (`local`) base means the whole wiki's links will expand to a
dead host, and leaving the `[Source:]` tags in place keeps that visible to the layout
lint instead of burying it in links that only look right.

Usage: python3 convert_source_tags.py --wiki-dir <dir> [--repo-json <path>]
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections.abc import Callable
from typing import Any

# `[Source: …]` as a whole; the inner text is split on commas and handled per item.
# Item forms: path · path:L42 · path:42 · path:L42-L50 · path:1-4.
TAG = re.compile(r"\[Source:\s*([^\]]+?)\]", re.IGNORECASE)
ENTRY = re.compile(r"^(.+?)(?::L?([0-9]+)(?:-L?[0-9]+)?)?\Z", re.IGNORECASE)
# Prose citations ("IMPORTS_FROM 엣지 기반") and bare line numbers are not paths and
# must be left alone. CJK text is the reliable signal; the word list catches the rest.
NON_FILE = re.compile(r"[가-힣ㄱ-ㅎㅏ-ㅣ一-龯]|\s(엣지|기반|구조|기준|디렉토리|폴더|내용|참조)\b")
LINE_ONLY = re.compile(r"^L?[0-9]+\Z", re.IGNORECASE)
# The `local` host is prepare's fallback when no remote could be resolved; a URL built
# on it would be dead, so conversion is skipped entirely.
LOCAL_BASE = re.compile(r"^https?://local(/|\Z)")

SKIP_DIRS = {".ast", ".trust", ".claims", ".analysis", ".git", "node_modules"}


def parse_args(argv: list[str]) -> dict[str, str | bool]:
    """Parse ``--key value`` / ``--flag`` pairs; a flag without a value becomes True."""
    args: dict[str, str | bool] = {}
    i = 0
    while i < len(argv):
        k = argv[i]
        if not k.startswith("--"):
            i += 1
            continue
        nxt = argv[i + 1] if i + 1 < len(argv) else None
        if not nxt or nxt.startswith("--"):
            args[k[2:]] = True
        else:
            args[k[2:]] = nxt
            i += 1
        i += 1
    return args


def opt(args: dict[str, str | bool], key: str) -> str | None:
    """Value of ``--key`` when it was given with a non-empty string."""
    value = args.get(key)
    return value if isinstance(value, str) and value else None


def walk(dir_: str, out: list[str] | None = None) -> list[str]:
    """Every ``.md`` file under ``dir_``, skipping generated trees and symlinks."""
    if out is None:
        out = []
    for e in sorted(os.scandir(dir_), key=lambda x: x.name):
        if e.is_dir(follow_symlinks=False):
            if e.name in SKIP_DIRS or e.name.startswith("."):
                continue
            walk(e.path, out)
        elif e.is_file(follow_symlinks=False) and e.name.endswith(".md"):
            out.append(e.path)
    return out


def read_repo_json(path: str) -> dict[str, Any] | None:
    """repo.json as a dict, or None when it cannot be read or parsed.

    A JSON document that is not an object still counts as readable — it simply has
    no ``deepLink``, which the caller reports as an unresolved base.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            raw = json.loads(f.read())
    except (OSError, ValueError):
        return None
    return raw if isinstance(raw, dict) else {}


def convert_file(path: str,
                 convert_tag: Callable[[str], str | None]) -> int:
    """Rewrite one page in place; returns how many citations were converted."""
    with open(path, encoding="utf-8", errors="replace") as f:
        src = f.read()
    converted = 0

    def replace(m: re.Match[str]) -> str:
        nonlocal converted
        inner = m.group(1)
        rep = convert_tag(inner)
        if rep is None:
            return m.group(0)
        # Counts comma-separated items, so a multi-file citation counts as many.
        converted += inner.count(",") + 1
        return rep

    out = TAG.sub(replace, src)
    if converted > 0:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(out)
    return converted


def main() -> int:
    args = parse_args(sys.argv[1:])
    wiki_dir_arg = opt(args, "wiki-dir")
    if not wiki_dir_arg:
        print("usage: python3 convert_source_tags.py --wiki-dir <dir> [--repo-json <path>]",
              file=sys.stderr)
        return 2
    wiki_dir = os.path.abspath(wiki_dir_arg)
    repo_json_arg = opt(args, "repo-json")
    repo_json_path = os.path.abspath(repo_json_arg) if repo_json_arg \
        else os.path.join(wiki_dir, "repo.json")

    repo_json = read_repo_json(repo_json_path)
    if repo_json is None:
        print(f"[convert-source-tags] repo.json 을 읽을 수 없습니다: {repo_json_path} "
              f"— 변환 건너뜀", file=sys.stderr)
        return 0
    deep_link = repo_json.get("deepLink")
    deep_link = deep_link if isinstance(deep_link, dict) else {}

    base = deep_link.get("base")
    base = base if isinstance(base, str) else ""
    if not base or LOCAL_BASE.search(base):
        print(f"[convert-source-tags] deepLink.base 미해석({base or 'none'}) — 변환 건너뜀. "
              f"repo.json 의 remote/deepLink 를 먼저 바로잡으세요.", file=sys.stderr)
        return 0

    def to_link(raw_path: str, line: str | None) -> str:
        p = re.sub(r"^/+", "", raw_path.strip())     # leading slashes → repo-relative
        # The host prefix is added at render time from `deepLink`, so the citation is
        # written in the compact `src:` form (issue #54).
        url = f"src:{p}#L{line}" if line else f"src:{p}"
        return f"[`{p}`]({url})"

    def convert_tag(inner: str) -> str | None:
        """One `[Source: …]` tag → deep-link(s), or None to leave it untouched.

        If any item is not usable as a path the whole tag is kept, so a partial
        conversion can never garble the sentence.
        """
        parts = [s for s in (t.strip() for t in inner.split(",")) if s]
        links: list[str] = []
        for part in parts:
            m = ENTRY.match(part)
            p = m.group(1).strip() if m else ""
            if not m or not p or LINE_ONLY.match(p) or NON_FILE.search(p):
                return None
            links.append(to_link(p, m.group(2)))
        return ", ".join(links) if links else None

    files = 0
    converted = 0
    for fp in walk(wiki_dir):
        n = convert_file(fp, convert_tag)
        if n > 0:
            files += 1
            converted += n
    print(f"[convert-source-tags] {converted} 개 [Source:] → deep-link "
          f"(파일 {files}개). base={base}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
