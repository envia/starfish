#!/usr/bin/env python3
"""L3 symbol coverage: does the wiki mention every symbol it is supposed to describe?

The public architecture surface is enumerated from the AST extraction output
(``api.json``, and/or a graphify ``graph.json``) and each symbol is grepped for in the
concatenated markdown. This is a *recall* signal — "the wiki covers the whole public
API" — and it is fully deterministic, with no LLM involved.

Two limits are inherent to the method: a single mention scores a full point, so how
*well* a symbol is documented is not measured, and same-named exports from different
packages are not told apart.

Usage:
  python3 validate_symbol_coverage.py [<api-json>] <wiki-dir> [--graph-json <path>]
    [--threshold 0.8] [--surface-profile architecture|all] [--top 30]

  <api-json>         api.json in ``files[].exports[]`` form. Optional — a repo the
                     TypeScript extractor cannot read can pass only --graph-json.
  <wiki-dir>         wiki root; every ``.md`` below it is read
  --graph-json       graphify graph.json (NetworkX node_link_data), which also covers
                     C/C++ and other languages. Its function labels are unioned into
                     the symbol list, alone or together with api.json.
  --threshold        passing coverage ratio (default 0.8)
  --surface-profile  ``architecture`` (default) drops test/config/generated exports
                     and, when the wiki links source files at all, narrows the
                     denominator to the exports of those files. ``all`` uses every
                     symbol name found in the inputs.
  --top              how many uncovered symbols to list (default 30)
"""

from __future__ import annotations

import json
import os
import re
import sys
import traceback
from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

CONFIG_FILE_RE = re.compile(
    r"(^|/)(eslint|vite|vitest|tsup|postcss|tailwind|playwright|jest|rollup|webpack"
    r"|babel|prettier|commitlint)\.config\.[cm]?[jt]s$", re.IGNORECASE)
TEST_FILE_RE = re.compile(
    r"(^|/)(test|tests|__tests__|__mocks__)/|[._-](test|spec)\.[cm]?[jt]sx?$",
    re.IGNORECASE)
GENERATED_FILE_RE = re.compile(
    r"(^|/)(dist|build|coverage|generated|fixtures?|mocks?)/", re.IGNORECASE)
# Expression kinds that are exported values rather than architecture surface.
NON_ARCHITECTURE_KIND = {
    "ArrayLiteralExpression",
    "CallExpression",
    "ObjectLiteralExpression",
}
_FILE_EXT_RE = re.compile(
    r"\.(c|h|cpp|hpp|cc|hh|py|sh|rs|m|md|json|inc|ts|tsx|js|mjs|cjs|go|java|kt|swift)$",
    re.IGNORECASE)

DEFAULT_THRESHOLD = 0.8
DEFAULT_TOP = 30


def parse_args(argv: list[str]) -> dict[str, Any]:
    """Parse ``--key value`` / ``--flag`` pairs plus positionals.

    A flag given without a value becomes the string ``"true"``, which the profile
    check below rejects rather than silently treating as a default.
    """
    out: dict[str, Any] = {"positional": []}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            k = a[2:]
            nxt = argv[i + 1] if i + 1 < len(argv) else None
            if nxt and not nxt.startswith("--"):
                i += 1
                out[k] = argv[i]
            else:
                out[k] = "true"
        else:
            out["positional"].append(a)
        i += 1
    return out


def parse_ratio(value: str | None, default: float) -> float:
    """A ``--threshold``-style ratio, falling back to the default when unparsable.

    Falling back matters: treating a typo as "no threshold" would silently disable
    the gate.
    """
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def parse_top(value: str | None, default: int) -> int:
    """``--top`` as a non-negative row limit, falling back to the default."""
    if value is None:
        return default
    m = re.match(r"\s*([0-9]+)", value)
    return int(m.group(1)) if m else default


def format_pct(x: float, digits: int) -> str:
    """A percentage to ``digits`` decimals, with ties rounded up.

    Ties are reached at realistic denominators (13/16 → 81.25), and the built-in
    formatter would resolve them to even and report 81.2.
    """
    q = Decimal(x).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
    return format(q, "f")


def parse_int_or_zero(s: str) -> int:
    """Leading integer of a string, or 0 — graphify locations look like ``L123``."""
    m = re.match(r"\s*([+-]?[0-9]+)", s)
    return int(m.group(1)) if m else 0


def walk_markdown(dir_: str) -> Iterator[str]:
    """Every ``.md`` under ``dir_``, skipping dot-dirs (bar ``.code-wiki``) and symlinks."""
    try:
        entries = list(os.scandir(dir_))
    except OSError:
        return
    for e in entries:
        if e.name.startswith(".") and e.name != ".code-wiki":
            continue
        if e.name == "node_modules":
            continue
        fp = os.path.join(dir_, e.name)
        if e.is_dir(follow_symlinks=False):
            yield from walk_markdown(fp)
        elif e.is_file(follow_symlinks=False) and fp.endswith(".md"):
            yield fp


def aggregate_wiki(wiki_dir: str) -> tuple[str, int]:
    """The whole wiki as one searchable buffer, plus the page count."""
    chunks: list[str] = []
    file_count = 0
    for fp in walk_markdown(wiki_dir):
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                chunks.append(f.read())
            file_count += 1
        except OSError:
            pass
    return "\n\n---\n\n".join(chunks), file_count


def collect_referenced_source_files(buffer: str, api: dict[str, Any]) -> set[str]:
    """api.json paths that appear verbatim somewhere in the wiki.

    Both deep-link URLs and plain markdown links embed the repo-relative path as-is,
    so matching known api paths stays deterministic without having to guess branch
    names or host URL formats.
    """
    out: set[str] = set()
    for f in (api.get("files") or []):
        if f.get("path") and f["path"] in buffer:
            out.add(f["path"])
    return out


def collect_symbols(api: dict[str, Any], profile: str, referenced_files: set[str],
                    ) -> tuple[dict[str, Any], dict[str, Any]]:
    """Symbols the wiki should cover, plus a breakdown of what the profile excluded.

    One name can be exported from several files, so only the observations that pass
    the profile are unioned; re-export and alias chains are not followed, which is
    hard to do deterministically and rarely changes the outcome.
    """
    seen: dict[str, Any] = {}   # name → {kind, files: [path, ...], line}
    stats: dict[str, Any] = {
        "raw": 0,
        "eligible": 0,
        "excluded": {
            "default": 0,
            "test": 0,
            "config": 0,
            "generated": 0,
            "kind": 0,
            "unreferencedFile": 0,
        },
        "referencedFiles": len(referenced_files),
    }
    for f in (api.get("files") or []):
        for ex in (f.get("exports") or []):
            stats["raw"] += 1
            if not ex.get("name"):
                continue
            if profile != "all":
                file_path = f.get("path") or ""
                if ex["name"] == "default":
                    stats["excluded"]["default"] += 1
                    continue
                if ex.get("is_test") or TEST_FILE_RE.search(file_path):
                    stats["excluded"]["test"] += 1
                    continue
                if CONFIG_FILE_RE.search(file_path):
                    stats["excluded"]["config"] += 1
                    continue
                if GENERATED_FILE_RE.search(file_path):
                    stats["excluded"]["generated"] += 1
                    continue
                if ex.get("kind") in NON_ARCHITECTURE_KIND:
                    stats["excluded"]["kind"] += 1
                    continue
                if len(referenced_files) > 0 and file_path not in referenced_files:
                    stats["excluded"]["unreferencedFile"] += 1
                    continue
            stats["eligible"] += 1
            if ex["name"] not in seen:
                seen[ex["name"]] = {"kind": ex.get("kind"), "files": [f.get("path")],
                                    "line": ex.get("line")}
            else:
                seen[ex["name"]]["files"].append(f.get("path"))
    return seen, stats


def collect_symbols_from_graphify(graph: dict[str, Any]) -> dict[str, Any]:
    """Function/symbol nodes of a graphify graph.

    A node whose label ends in a source extension is the *file itself*, not a symbol,
    and a trailing argument list is stripped (``foo_get_int()`` → ``foo_get_int``).
    """
    seen: dict[str, Any] = {}
    for n in (graph.get("nodes") or []):
        if n.get("file_type") != "code":
            continue
        raw = n.get("label")
        if raw is None:
            raw = n.get("norm_label")
        if raw is None:
            raw = n.get("id")
        if raw is None:
            raw = ""
        name = str(raw).strip()
        if not name:
            continue
        if _FILE_EXT_RE.search(name):
            continue
        name = re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()
        if not name or re.search(r"\s", name):
            continue           # a label with whitespace is prose, not a symbol
        loc = n.get("source_location")
        line = parse_int_or_zero(re.sub(r"^L", "", str(loc if loc is not None else "L0")))
        src = n.get("source_file")
        if src is None:
            src = ""
        if name not in seen:
            seen[name] = {"kind": "graphify", "files": [src], "line": line}
        else:
            seen[name]["files"].append(src)
    return seen


def union_symbols(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Merge two symbol maps: same name keeps the first kind/line and merges files."""
    out = dict(a)
    for name, info in b.items():
        if name not in out:
            out[name] = {**info, "files": list(info["files"])}
        else:
            out[name]["files"].extend(info["files"])
    return out


def is_covered(symbol_name: str, buffer: str) -> bool:
    """Whether the wiki mentions a symbol.

    Matching is on identifier boundaries, so a namespaced mention (``Foo.bar``) counts
    for ``bar`` too. Names shorter than 3 characters only count when explicitly
    backticked — a bare ``id`` would otherwise match inside ordinary prose.
    """
    if len(symbol_name) < 3:
        return ("`" + symbol_name + "`") in buffer
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(symbol_name)}(?![A-Za-z0-9_])",
                     buffer) is not None


def main() -> int:
    args = parse_args(sys.argv[1:])
    # Positionals come in two shapes: `<api-json> <wiki-dir>`, or just `<wiki-dir>`
    # when the surface comes from --graph-json instead.
    api_json = None
    wiki_dir = None
    if len(args["positional"]) == 2:
        api_json, wiki_dir = args["positional"]
    elif len(args["positional"]) == 1:
        wiki_dir = args["positional"][0]
    else:
        print("Usage: python3 validate_symbol_coverage.py [<api-json>] <wiki-dir> "
              "[--graph-json X] [--threshold 0.8] "
              "[--surface-profile architecture|all] [--top 30]", file=sys.stderr)
        return 2
    graph_json = args.get("graph-json")
    if not wiki_dir:
        print("Missing <wiki-dir>", file=sys.stderr)
        return 2
    if not api_json and not graph_json:
        print("Must provide <api-json> (positional) or --graph-json (or both)",
              file=sys.stderr)
        return 2
    threshold = parse_ratio(args.get("threshold"), DEFAULT_THRESHOLD)
    top_n = parse_top(args.get("top"), DEFAULT_TOP)
    surface_profile = args.get("surface-profile", "architecture")
    if surface_profile not in ("architecture", "all"):
        print(f"Invalid --surface-profile: {surface_profile} "
              f"(expected architecture|all)", file=sys.stderr)
        return 2

    buffer, file_count = aggregate_wiki(wiki_dir)
    if file_count == 0:
        print(f"No markdown files found under {wiki_dir}", file=sys.stderr)
        return 3

    symbols: dict[str, Any] = {}
    sources: list[str] = []
    api_stats: dict[str, Any] | None = None

    if api_json:
        try:
            with open(api_json, encoding="utf-8", errors="replace") as f:
                api = json.loads(f.read())
        except Exception as e:
            print(f"Failed to read API json: {e}", file=sys.stderr)
            return 3
        referenced_files = collect_referenced_source_files(buffer, api)
        api_syms, stats = collect_symbols(api, surface_profile, referenced_files)
        api_stats = stats
        symbols = union_symbols(symbols, api_syms)
        sources.append(f"api-json ({len(api_syms)}/{stats['raw']} exports, "
                       f"profile={surface_profile})")

    if graph_json:
        try:
            with open(graph_json, encoding="utf-8", errors="replace") as f:
                graph = json.loads(f.read())
        except Exception as e:
            print(f"Failed to read graph json: {e}", file=sys.stderr)
            return 3
        before = len(symbols)
        graph_syms = collect_symbols_from_graphify(graph)
        symbols = union_symbols(symbols, graph_syms)
        sources.append(f"graphify ({len(graph_syms)} symbols, "
                       f"+{len(symbols) - before} new)")

    if len(symbols) == 0:
        # An empty denominator (no symbol extracted) is N/A, not a failure.
        print("[symbol-coverage] N/A — no symbols found in inputs", file=sys.stderr)
        return 0

    covered: dict[str, Any] = {}
    uncovered: dict[str, Any] = {}
    for name, info in symbols.items():
        if is_covered(name, buffer):
            covered[name] = info
        else:
            uncovered[name] = info

    total = len(symbols)
    coverage_ratio = len(covered) / total

    print("L3 Symbol Coverage")
    print(f"  sources:  {' + '.join(sources)}")
    print(f"  wiki:     {wiki_dir} ({file_count} .md files)")
    print(f"  profile:  {surface_profile}")
    if api_stats and surface_profile != "all":
        ex = api_stats["excluded"]
        print(f"  api raw:  {api_stats['raw']} exports; eligible observations: "
              f"{api_stats['eligible']}; referenced files: "
              f"{api_stats['referencedFiles'] or 'all'}")
        print(f"  excluded: default:{ex['default']} test:{ex['test']} "
              f"config:{ex['config']} generated:{ex['generated']} kind:{ex['kind']} "
              f"unreferenced-file:{ex['unreferencedFile']}")
    print(f"  symbols:  {total} total")
    print(f"  covered:  {len(covered)}  ({format_pct(coverage_ratio * 100, 1)}%)")
    print(f"  missing:  {len(uncovered)}")
    print(f"  threshold: {format_pct(threshold * 100, 0)}%")
    print()

    if len(uncovered) > 0:
        by_dir: dict[str, int] = {}
        for info in uncovered.values():
            file0 = info["files"][0] or ""
            top_dir = "/".join(file0.split("/")[:2]) or "(root)"
            by_dir[top_dir] = by_dir.get(top_dir, 0) + 1
        print("  missing 분포 (top-level dir):")
        for dir_, n in sorted(by_dir.items(), key=lambda kv: kv[1], reverse=True):
            print(f"    {dir_.ljust(40)} {n}")
        print()

        print(f"  미커버 상위 {min(top_n, len(uncovered))}개:")
        for name, info in list(uncovered.items())[:top_n]:
            kind = "-" if info["kind"] is None else str(info["kind"])
            line = "-" if info["line"] is None else info["line"]
            loc = f"{info['files'][0] or ''}:{line}"
            print(f"    {kind.ljust(20)} {name.ljust(36)} {loc}")

    if coverage_ratio < threshold:
        print(f"\n❌ coverage {format_pct(coverage_ratio * 100, 1)}% < threshold "
              f"{format_pct(threshold * 100, 0)}%", file=sys.stderr)
        return 1
    print(f"\n✅ coverage {format_pct(coverage_ratio * 100, 1)}% ≥ threshold "
          f"{format_pct(threshold * 100, 0)}%")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        sys.exit(3)
