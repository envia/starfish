#!/usr/bin/env python3
"""Quote mermaid graph/flowchart labels that would otherwise fail to parse.

``mermaidSyntax`` is a hard gate, and a single unquoted special character (`/`,
a space, `.`, `:`, `()`) in an edge or node label breaks mermaid v10 — which the
viewer loads from a CDN. The generation guideline asks for quoted labels, but it is
easy to miss, so finalize freezes them here.

* Only ``graph`` / ``flowchart`` blocks are touched. sequenceDiagram, classDiagram,
  erDiagram and friends have different grammars and are left alone.
* Labels that are already quoted, or that contain nothing but word characters and
  hyphens, are left as they are.
* ``verification/validate_mermaid.py`` remains the authority: whatever this tool
  cannot fix safely, that validator reports.

Usage: python3 quote_mermaid_labels.py --wiki-dir <dir>
"""

from __future__ import annotations

import os
import re
import sys

SKIP_DIRS = {".ast", ".trust", ".claims", ".analysis", ".git", "node_modules"}

# A label needs quoting as soon as it holds anything other than word characters or a
# hyphen — a space, `/`, `.`, `:`, parentheses, CJK text, …
NEEDS_QUOTE = re.compile(r"[^A-Za-z0-9_-]")

# Single-shape node labels: `id[..]`, `id(..)`, `id{..}`. The inner text may not
# contain any bracket or quote, which means compound shapes (`[[..]]`, `[(..)]`,
# `((..))`) never match and are left untouched — rewriting them risks corrupting the
# diagram, so validate_mermaid reports those instead.
# The lookbehind restricts matches to a shape attached to a node id (`MCPServer[..]`),
# so subgraph titles, standalone parentheses and comments are not rewritten. It is
# ASCII-only on purpose: a CJK node id is not an identifier mermaid accepts here.
NODE_SHAPES = [
    re.compile(r'(?<=[A-Za-z0-9_])(\[)([^\[\](){}"]+?)(\])'),
    re.compile(r'(?<=[A-Za-z0-9_])(\()([^\[\](){}"]+?)(\))'),
    re.compile(r'(?<=[A-Za-z0-9_])(\{)([^\[\](){}"]+?)(\})'),
]
# Edge labels: `-->|label|`. In graph syntax `|` is only ever an edge-label delimiter.
PIPE_LABEL = re.compile(r"\|([^|]+)\|")
FIRST_LINE_TYPE = re.compile(r"^(graph|flowchart)(?![A-Za-z0-9_])", re.IGNORECASE)
TYPE_LINE = re.compile(r"^\s*(graph|flowchart)(?![A-Za-z0-9_])", re.IGNORECASE)
MERMAID_BLOCK = re.compile(r"```mermaid\s*\n([\s\S]*?)\n```")


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


def wrap(inner: str) -> str | None:
    """Quoted form of a label, or None when it must stay as it is."""
    t = inner.strip()
    if not t:
        return None
    if t.startswith('"') and t.endswith('"'):
        return None                      # already quoted
    if not NEEDS_QUOTE.search(t):
        return None                      # no quoting needed
    return '"' + t.replace('"', "'") + '"'


def quote_line(line: str) -> str:
    """Quote every edge and node label on one diagram line."""
    def pipe(m: re.Match[str]) -> str:
        w = wrap(m.group(1))
        return f"|{w}|" if w else m.group(0)

    def shape(m: re.Match[str]) -> str:
        w = wrap(m.group(2))
        return f"{m.group(1)}{w}{m.group(3)}" if w else m.group(0)

    out = PIPE_LABEL.sub(pipe, line)
    for pattern in NODE_SHAPES:
        out = pattern.sub(shape, out)
    return out


def process_block(block: str) -> tuple[str, int]:
    """Quote labels in one mermaid block; returns (block, changed line count)."""
    lines = block.split("\n")
    first = next((line for line in lines if line.strip()), "").strip()
    if not FIRST_LINE_TYPE.search(first):
        return block, 0
    changed = 0
    out_lines: list[str] = []
    for line in lines:
        if TYPE_LINE.search(line):
            out_lines.append(line)       # the diagram-type declaration stays verbatim
            continue
        q = quote_line(line)
        if q != line:
            changed += 1
        out_lines.append(q)
    return "\n".join(out_lines), changed


def process_file(path: str) -> int:
    """Rewrite one page in place; returns how many label lines were quoted."""
    with open(path, encoding="utf-8", errors="replace") as f:
        src = f.read()
    edits = 0

    def replace(m: re.Match[str]) -> str:
        nonlocal edits
        block, changed = process_block(m.group(1))
        edits += changed
        return "```mermaid\n" + block + "\n```" if changed else m.group(0)

    out = MERMAID_BLOCK.sub(replace, src)
    if edits > 0:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(out)
    return edits


def main() -> int:
    args = parse_args(sys.argv[1:])
    wiki_dir_arg = opt(args, "wiki-dir")
    if not wiki_dir_arg:
        print("usage: python3 quote_mermaid_labels.py --wiki-dir <dir>", file=sys.stderr)
        return 2
    wiki_dir = os.path.abspath(wiki_dir_arg)

    files = 0
    edits = 0
    for fp in walk(wiki_dir):
        n = process_file(fp)
        if n > 0:
            files += 1
            edits += n
    print(f"[quote-mermaid-labels] {edits} 개 라벨 라인 인용 처리 (파일 {files}개)",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
