#!/usr/bin/env python3
"""Fail fast when ``.ast/api.json`` or ``.ast/deps.json`` is missing or empty.

Everything downstream (grounding, symbol coverage, diagram accuracy) grades the wiki
against these two files, so an empty extraction has to stop the pipeline here rather
than turn into a wiki full of unverifiable claims.

"Empty" only counts as a failure when the repo does contain source files the extractor
should have handled — a repo with no supported source at all is legitimately empty.

Usage: python3 validate_ast_baseline.py --repo-root <source> --wiki-dir <wiki>
         [--api-json X --deps-json Y]
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

TS_EXT = {".ts", ".tsx", ".js", ".mjs", ".cjs"}
C_EXT = {".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh", ".hxx"}
PHP_EXT = {".php"}
SKIP_DIRS = {
    "node_modules", "vendor", "storage", "bootstrap", "public", "dist", "build",
    "coverage", "_archive",
}


def parse_args(argv: list[str]) -> dict[str, str | bool]:
    """Parse ``--key value`` / ``--flag`` pairs; a flag without a value becomes True."""
    args: dict[str, str | bool] = {}
    i = 0
    while i < len(argv):
        key = argv[i]
        if not key.startswith("--"):
            i += 1
            continue
        nxt = argv[i + 1] if i + 1 < len(argv) else None
        if not nxt or nxt.startswith("--"):
            args[key[2:]] = True
        else:
            args[key[2:]] = nxt
            i += 1
        i += 1
    return args


def opt(args: dict[str, str | bool], key: str) -> str | None:
    """Value of ``--key`` when it was given with a non-empty string."""
    value = args.get(key)
    return value if isinstance(value, str) and value else None


def usage(message: str | None = None) -> None:
    if message:
        print(f"error: {message}", file=sys.stderr)
    print("usage: python3 validate_ast_baseline.py --repo-root <source> "
          "--wiki-dir <wiki> [--api-json X --deps-json Y]", file=sys.stderr)
    sys.exit(2)


def read_json(file: str) -> dict[str, Any]:
    """Parsed JSON, or ``{"__error": <reason>}`` so the caller can report it."""
    try:
        with open(file, encoding="utf-8", errors="replace") as f:
            return json.loads(f.read())
    except Exception as error:
        return {"__error": str(error)}


def count_symbols(api: dict[str, Any]) -> int:
    total = 0
    for file in (api.get("files") or []):
        exports = file.get("exports")
        total += len(exports) if isinstance(exports, list) else 0
    return total


def count_deps(deps: dict[str, Any]) -> int:
    internal = deps.get("internal")
    external = deps.get("external")
    return (len(internal) if isinstance(internal, list) else 0) \
        + (len(external) if isinstance(external, list) else 0)


def detect_supported_counts(repo_root: str) -> dict[str, int]:
    """Source files per supported language, found with a plain filesystem walk."""
    counts = {"ts": 0, "c": 0, "php": 0}

    def walk(dir_: str) -> None:
        try:
            entries = list(os.scandir(dir_))
        except OSError:
            return
        for e in entries:
            if e.is_dir(follow_symlinks=False):
                if e.name in SKIP_DIRS or e.name.startswith("."):
                    continue
                walk(os.path.join(dir_, e.name))
            elif e.is_file(follow_symlinks=False):
                if e.name.endswith(".d.ts"):
                    continue
                dot = e.name.rfind(".")
                if dot < 0:
                    continue
                ext = e.name[dot:]
                if ext in TS_EXT:
                    counts["ts"] += 1
                elif ext in C_EXT:
                    counts["c"] += 1
                elif ext in PHP_EXT:
                    counts["php"] += 1
    walk(repo_root)
    return counts


def primary_language(counts: dict[str, int]) -> str:
    """The language with the most files; a tie is broken by name, so it is stable."""
    entries = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return entries[0][0] if entries and entries[0][1] > 0 else "none"


def main() -> int:
    args = parse_args(sys.argv[1:])
    repo_root_arg = opt(args, "repo-root")
    wiki_dir_arg = opt(args, "wiki-dir")
    if not repo_root_arg or not wiki_dir_arg:
        usage("missing --repo-root or --wiki-dir")
        return 2

    repo_root = os.path.abspath(repo_root_arg)
    wiki_dir = os.path.abspath(wiki_dir_arg)
    api_json_arg = opt(args, "api-json")
    deps_json_arg = opt(args, "deps-json")
    api_json = os.path.abspath(api_json_arg or os.path.join(wiki_dir, ".ast", "api.json"))
    deps_json = os.path.abspath(deps_json_arg
                                or os.path.join(wiki_dir, ".ast", "deps.json"))

    failures: list[str] = []
    if not os.path.exists(api_json):
        failures.append(f"missing api.json: {api_json}")
    if not os.path.exists(deps_json):
        failures.append(f"missing deps.json: {deps_json}")

    api: dict[str, Any] = read_json(api_json) if os.path.exists(api_json) \
        else {"files": []}
    deps: dict[str, Any] = read_json(deps_json) if os.path.exists(deps_json) \
        else {"internal": [], "external": []}
    if api.get("__error"):
        failures.append(f"invalid api.json: {api['__error']}")
    if deps.get("__error"):
        failures.append(f"invalid deps.json: {deps['__error']}")

    counts = detect_supported_counts(repo_root)
    primary = primary_language(counts)
    symbols = 0 if api.get("__error") else count_symbols(api)
    dep_edges = 0 if deps.get("__error") else count_deps(deps)
    supported_files = counts["ts"] + counts["c"] + counts["php"]

    if supported_files > 0:
        if symbols == 0:
            failures.append("empty api.json: no exported/public symbols found")
        if dep_edges == 0:
            failures.append("empty deps.json: no dependency edges found")

    print("AST baseline")
    print(f"  repo:     {repo_root}")
    print(f"  wiki:     {wiki_dir}")
    print(f"  primary:  {primary}")
    print(f"  sources:  ts/js={counts['ts']} c/c++={counts['c']} php={counts['php']}")
    print(f"  api:      {symbols} symbols")
    print(f"  deps:     {dep_edges} edges")

    if len(failures) > 0:
        print("  status:   fail")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("  status:   pass")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
