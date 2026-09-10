#!/usr/bin/env python3
"""Lint the ```mermaid blocks of a markdown page for mermaid v10 compatibility.

The wiki viewer loads mermaid from a CDN, and v10 rejects edge labels that newer
versions happily parse — so a diagram that looks fine locally can still render as
"Syntax error in text" for readers. This is a regex lint rather than a real parse:
it deliberately flags only what v10's parser is known to reject, so it can never fail
a valid document.

Usage: python3 validate_mermaid.py <file.md> [<file.md> ...]
"""

from __future__ import annotations

import re
import sys
import traceback
from typing import Any

_BLOCK_OPEN_RE = re.compile(r"^```mermaid\s*$")
_BLOCK_CLOSE_RE = re.compile(r"^```\s*$")
_DOTTED_RE = re.compile(r"-\.\s*([^.\n]*?(?:\.[^.\n]*?)*?)\s*\.->")
_PIPE_RE = re.compile(r"(?:-->|<--|---|<-\.|\.->)\|([^|]+)\|")
_THICK_RE = re.compile(r"==\s*([^=\n]+?)\s*==>")

# Only unquoted parentheses actually break the v10 parser — verified with mermaid.parse
# on 10.0.2 (all three edge forms fail) and 10.9.6 (the pipe form still fails). `/` `.`
# `:` used to be flagged here too, but real-parser runs show they parse fine across the
# whole v10 range (and on v11/GitHub), so flagging them hard-failed valid documents.
RISKY_CHARS = re.compile(r"[()]")


def extract_blocks(text: str) -> list[dict[str, Any]]:
    """Every ```mermaid block with its 1-based line span and body."""
    lines = text.split("\n")
    blocks: list[dict[str, Any]] = []
    in_block = False
    start = -1
    buf: list[str] = []
    for i, line in enumerate(lines):
        if not in_block:
            if _BLOCK_OPEN_RE.match(line):
                in_block = True
                start = i + 1
                buf = []
        else:
            if _BLOCK_CLOSE_RE.match(line):
                blocks.append({"startLine": start + 1, "endLine": i,
                               "code": "\n".join(buf)})
                in_block = False
            else:
                buf.append(line)
    if in_block:
        blocks.append({
            "startLine": start + 1,
            "endLine": len(lines),
            "code": "\n".join(buf),
            "unterminated": True,
        })
    return blocks


def lint_v10_compat(code: str) -> list[dict[str, Any]]:
    """Edge labels that mermaid v10 cannot parse, in the three labelled edge forms:
    ``A -.LABEL.-> B``, ``A -->|LABEL| B`` and ``A ==LABEL==> B``."""
    issues: list[dict[str, Any]] = []
    forms = [
        (_DOTTED_RE, "dotted-edge", '-. "{}" .->'),
        (_PIPE_RE, "pipe-edge", '|"{}"|'),
        (_THICK_RE, "thick-edge", '== "{}" ==>'),
    ]
    for i, line in enumerate(code.split("\n")):
        for pattern, kind, suggest in forms:
            for m in pattern.finditer(line):
                label = (m.group(1) or "").strip()
                if not label or label.startswith('"'):
                    continue
                risky = RISKY_CHARS.search(label)
                if risky:
                    issues.append({"lineOffset": i, "kind": kind,
                                   "chars": risky.group(0),
                                   "suggest": suggest.format(label)})
    return issues


def validate_file(file_path: str) -> dict[str, Any]:
    """Lint one page. ``skipped`` means it holds nothing to check."""
    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:
        return {"skipped": True, "reason": f"read failed: {e}"}
    if not file_path.endswith(".md"):
        return {"skipped": True, "reason": "not a markdown file"}
    if "```mermaid" not in text:
        return {"skipped": True, "reason": "no mermaid block"}

    blocks = extract_blocks(text)
    failures: list[dict[str, Any]] = []

    for i, b in enumerate(blocks):
        if b.get("unterminated"):
            failures.append({
                "block": i + 1,
                "line": b["startLine"],
                "error": "unterminated mermaid block (missing closing ```)",
            })
            continue
        for issue in lint_v10_compat(b["code"]):
            failures.append({
                "block": i + 1,
                "line": b["startLine"] + issue["lineOffset"],
                "error": f'v10-compat: {issue["kind"]} — edge label has unescaped '
                         f'`{issue["chars"]}` (wrap label in double-quotes: '
                         f'`{issue["suggest"]}`)',
            })

    return {"skipped": False, "blocks": len(blocks), "failures": failures}


def main() -> int:
    args = sys.argv[1:]
    if len(args) == 0:
        print("usage: python3 validate_mermaid.py <file.md> [<file.md> ...]", file=sys.stderr)
        return 2
    total_blocks = 0
    total_failures = 0
    files_with_blocks = 0
    per_file: list[dict[str, Any]] = []
    for fp in args:
        r = validate_file(fp)
        if r["skipped"]:
            continue
        files_with_blocks += 1
        total_blocks += r["blocks"]
        total_failures += len(r["failures"])
        if len(r["failures"]) > 0:
            per_file.append({"file": fp, **r})
    if total_failures == 0:
        if total_blocks > 0:
            print(f"[mermaid] ok — {total_blocks} block(s) v10-compat linted across "
                  f"{files_with_blocks} file(s)", file=sys.stderr)
        else:
            # No diagram anywhere → nothing to measure, not a pass.
            print("[mermaid] N/A — no mermaid block(s) found", file=sys.stderr)
        return 0
    print(f"[mermaid] FAIL — {total_failures} failing block(s) across "
          f"{len(per_file)} file(s) (scanned {total_blocks} block(s) in "
          f"{files_with_blocks} file(s))", file=sys.stderr)
    for f in per_file:
        print(f"\n  {f['file']}", file=sys.stderr)
        for fail in f["failures"]:
            print(f"    - block #{fail['block']} at L{fail['line']}", file=sys.stderr)
            print(f"      {fail['error']}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException:
        print(f"[mermaid] validator crashed: {traceback.format_exc().rstrip()}",
              file=sys.stderr)
        sys.exit(3)
