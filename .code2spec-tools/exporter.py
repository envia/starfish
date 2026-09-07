"""Export code graph to Markdown formats (raw data and Mermaid diagrams).

Performance-optimised for large projects (1M+ LOC):
- Parallel parsing with ProcessPoolExecutor (default: auto workers)
- Lazy dict-based merge (avoids NodeInfo/EdgeInfo object materialisation)
- JSON-first export (Markdown as derived artifact)
- Reverse-index Core/Mermaid generation (O(1) lookups, no O(N²) scans)
- os.scandir-based file collection (faster than rglob)
"""

from __future__ import annotations

import json
import logging
import os
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from .parser import EdgeInfo, NodeInfo
except ImportError:  # script/installed-tools flat execution
    from parser import EdgeInfo, NodeInfo


@dataclass
class CodeSize:
    """코드 규모 통계."""

    total_files: int
    total_lines: int
    total_bytes: int
    by_extension: dict[
        str, dict[str, int]
    ]  # {".py": {"files": 10, "lines": 500, "bytes": 15000}}


# ── Source file extensions and ignore patterns ────────────────────────────────

_SOURCE_EXTENSIONS = frozenset({
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".cs",
    ".rb", ".cpp", ".cc", ".cxx", ".c", ".h", ".hpp", ".kt", ".swift",
    ".php", ".sol", ".vue",
})

# Baseline exclusions, applied before any rule file. Rule files are folded on
# top and can re-include an entry here (e.g. `!bin` when `bin/` holds source).
_IGNORE_DIRS = frozenset({
    "node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build",
    ".next", "target", ".code-to-ast", "bin", "obj",
})

# Directories that mark a project root, bounding the upward search for rule
# files. `.p4config` is the p4 analogue of `.git`; without any marker (exported
# tarball, plain directory) only the analysis root itself is searched.
_ROOT_MARKERS = (".git", ".p4config", ".code2specignore")

# Rule file names in increasing precedence order: git, then p4, then ours.
_GIT_IGNORE_FILE = ".gitignore"
_P4_IGNORE_FILES = (".p4ignore", "p4ignore.txt")
_CODE2SPEC_IGNORE_FILE = ".code2specignore"


def export_graph(
    repo_root: Path,
    output_dir: Path | None = None,
    format: str = "both",
    min_lines: int = 0,
    workers: int = -1,
    cache_dir: Path | None = None,
    no_cache: bool = False,
    discovered_types_path: str | None = None,
    benchmark: bool = False,
) -> dict:
    """Parse source files and export graph as Markdown/JSON files.

    Args:
        repo_root: Repository root path.
        output_dir: Output directory (default: .code-to-ast/).
        format: Export format - "raw", "mermaid", or "both".
        workers: Number of parallel parsing workers (-1=auto, max 16).
        cache_dir: Directory for parse cache (default: .code-to-ast/.cache/).
        no_cache: Disable caching entirely.
        discovered_types_path: Path to LLM-discovered types JSON (deprecated).
        benchmark: Enable phase-level benchmark instrumentation.

    Returns:
        Summary with output file paths and statistics.
    """

    try:
        from .cache_manager import (
            ParseCache,
            build_updated_cache_from_dicts,
            find_changed_files,
            load_cache,
            merge_results_lazy,
            save_cache,
        )
    except ImportError:  # script/installed-tools flat execution
        from cache_manager import (
            ParseCache,
            build_updated_cache_from_dicts,
            find_changed_files,
            load_cache,
            merge_results_lazy,
            save_cache,
        )

    # ── Benchmark setup ────────────────────────────────────────────────────
    bench_report = None
    if benchmark:
        try:
            from .benchmark import (
                BenchmarkReport,
                _get_rss_kb,
                measure_artifact,
                phase,
                save_report,
            )
        except ImportError:
            from benchmark import BenchmarkReport, _get_rss_kb, measure_artifact, phase, save_report
        bench_report = BenchmarkReport()
        bench_report.workers = workers if workers > 0 else min(os.cpu_count() or 4, 16)

    total_start = time.perf_counter()

    if output_dir is None:
        output_dir = repo_root / ".code-to-ast"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Cache setup ────────────────────────────────────────────────────────
    cache_path = None
    cache = None
    if not no_cache and cache_dir is not None:
        cache_path = cache_dir / "parse-cache.json"
        cache = load_cache(cache_path) or ParseCache()
    elif not no_cache:
        cache_path = output_dir / ".cache" / "parse-cache.json"
        cache = load_cache(cache_path) or ParseCache()

    # ── Phase: Collect source files ─────────────────────────────────────────
    if bench_report:
        with phase(bench_report, "collect_files"):
            source_files = _collect_source_files(repo_root, min_lines=min_lines)
    else:
        source_files = _collect_source_files(repo_root, min_lines=min_lines)

    # ── Cache: find changed files ────────────────────────────────────────────
    changed_files = source_files
    cached_entries: list = []
    if cache is not None:
        changed_files, cached_entries = find_changed_files(source_files, cache)
        total_cached = len(cached_entries)
        total_changed = len(changed_files)
        print(
            f"[Export] Cache: {total_cached} cached, "
            f"{total_changed} changed/new"
        )
        if bench_report:
            hit_rate = total_cached / (total_cached + total_changed) if (total_cached + total_changed) > 0 else 0.0
            bench_report.cache_hit_rate = hit_rate

    # ── Phase: Parse files (parallel) ────────────────────────────────────────
    parse_results: list[tuple[list[NodeInfo], list[EdgeInfo]]] = []
    if changed_files:
        if bench_report:
            with phase(bench_report, "parse_files", items=len(changed_files)):
                parse_results = _parse_files_parallel(changed_files, workers, discovered_types_path)
        else:
            parse_results = _parse_files_parallel(changed_files, workers, discovered_types_path)

    # ── Phase: Merge results (lazy dict-based) ───────────────────────────────
    if bench_report:
        with phase(bench_report, "merge_results", items=len(cached_entries) + len(parse_results)):
            all_node_dicts, all_edge_dicts = merge_results_lazy(cached_entries, parse_results)
    else:
        all_node_dicts, all_edge_dicts = merge_results_lazy(cached_entries, parse_results)

    # ── Cache: update and save ───────────────────────────────────────────────
    if cache is not None and cache_path is not None and parse_results:
        # Collect new dicts for cache update
        new_node_dicts: list[dict] = []
        new_edge_dicts: list[dict] = []
        for nodes, edges in parse_results:
            new_node_dicts.extend(n.to_dict() for n in nodes)
            new_edge_dicts.extend(e.to_dict() for e in edges)
        cache = build_updated_cache_from_dicts(cache, new_node_dicts, new_edge_dicts, changed_files)
        save_cache(cache_path, cache)

    # ── Phase: Collect code size statistics ───────────────────────────────────
    if bench_report:
        with phase(bench_report, "collect_code_size", items=len(source_files)):
            code_size = _collect_code_size(source_files)
    else:
        code_size = _collect_code_size(source_files)

    total_nodes = len(all_node_dicts)
    total_edges = len(all_edge_dicts)

    # ── Generate output ──────────────────────────────────────────────────────
    results = {
        "files_parsed": len(source_files),
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "output_files": [],
        "code_size": {
            "total_files": code_size.total_files,
            "total_lines": code_size.total_lines,
            "total_bytes": code_size.total_bytes,
            "by_extension": code_size.by_extension,
        },
    }

    # ── Phase: JSON export (primary representation) ──────────────────────────
    json_path = output_dir / "graph-raw.json"
    if bench_report:
        with phase(bench_report, "export_json", items=total_nodes + total_edges):
            _export_json_dicts(all_node_dicts, all_edge_dicts, repo_root, json_path)
    else:
        _export_json_dicts(all_node_dicts, all_edge_dicts, repo_root, json_path)
    results["output_files"].append(str(json_path))
    results["json_path"] = str(json_path)
    if bench_report:
        measure_artifact(bench_report, "graph-raw.json", json_path)

    # ── Phase: Raw Markdown export (derived artifact, opt-in) ──────────────────
    if format in ("raw", "both"):
        raw_path = output_dir / "graph-raw.md"
        if bench_report:
            with phase(bench_report, "export_raw_md", items=total_nodes + total_edges):
                _export_raw_dicts(all_node_dicts, all_edge_dicts, repo_root, raw_path)
        else:
            _export_raw_dicts(all_node_dicts, all_edge_dicts, repo_root, raw_path)
        results["output_files"].append(str(raw_path))
        if bench_report:
            measure_artifact(bench_report, "graph-raw.md", raw_path)

    # ── Phase: Core selection (in-memory, from dicts) ─────────────────────────
    if bench_report:
        with phase(bench_report, "select_core"):
            core_files = _select_core_modules_from_dicts(all_node_dicts, all_edge_dicts, repo_root)
    else:
        core_files = _select_core_modules_from_dicts(all_node_dicts, all_edge_dicts, repo_root)
    results["core_files"] = core_files

    # ── Phase: Mermaid generation ─────────────────────────────────────────────
    if format in ("mermaid", "both"):
        mermaid_dir = output_dir / "graph-mermaid"
        mermaid_dir.mkdir(parents=True, exist_ok=True)
        if bench_report:
            with phase(bench_report, "export_mermaid"):
                if core_files:
                    output_files = _export_mermaid_core_dicts(
                        all_node_dicts, all_edge_dicts, core_files, repo_root, mermaid_dir
                    )
                else:
                    output_files = _export_mermaid_all_dicts(
                        all_node_dicts, all_edge_dicts, repo_root, mermaid_dir
                    )
        else:
            if core_files:
                output_files = _export_mermaid_core_dicts(
                    all_node_dicts, all_edge_dicts, core_files, repo_root, mermaid_dir
                )
            else:
                output_files = _export_mermaid_all_dicts(
                    all_node_dicts, all_edge_dicts, repo_root, mermaid_dir
                )
        results["output_files"].extend(output_files)

    # ── Phase: Summary JSON (lightweight, for module discovery) ──────────────
    summary_path = output_dir / "graph-summary.json"
    if bench_report:
        with phase(bench_report, "export_summary"):
            _export_summary_json(all_node_dicts, all_edge_dicts, code_size, repo_root, summary_path)
    else:
        _export_summary_json(all_node_dicts, all_edge_dicts, code_size, repo_root, summary_path)
    results["output_files"].append(str(summary_path))
    results["summary_path"] = str(summary_path)
    if bench_report:
        measure_artifact(bench_report, "graph-summary.json", summary_path)

    # ── Benchmark finalisation ───────────────────────────────────────────────
    if bench_report:
        bench_report.total_elapsed = time.perf_counter() - total_start
        bench_report.total_nodes = total_nodes
        bench_report.total_edges = total_edges
        try:
            bench_report.peak_rss_kb = _get_rss_kb()
        except Exception:
            pass
        bench_report.print_summary()
        bench_path = output_dir / "benchmark-report.json"
        save_report(bench_report, bench_path)
        results["benchmark"] = bench_report.to_dict()

    return results


def _parse_files_parallel(
    source_files: list[Path], workers: int = -1, discovered_types_path: str | None = None
) -> list[tuple[list[NodeInfo], list[EdgeInfo]]]:
    """Parse source files in parallel using ProcessPoolExecutor.

    Args:
        source_files: List of source file paths to parse.
        workers: Number of parallel workers. -1=auto (min(cpu_count, 16)), 1=serial.
        discovered_types_path: Deprecated, ignored.

    Returns:
        List of (nodes, edges) tuples, one per source file.
    """
    from concurrent.futures import ProcessPoolExecutor, as_completed
    try:
        from .parser import CodeParser
    except ImportError:  # script/installed-tools flat execution
        from parser import CodeParser

    # Resolve workers
    if workers <= 0:
        workers = min(os.cpu_count() or 4, 16)

    if workers <= 1:
        # Serial mode — no subprocess overhead
        parser = CodeParser()
        return [parser.parse_file(fp) for fp in source_files]

    # Parallel mode — preserve original file order via index mapping
    if discovered_types_path:
        logger.warning("discovered_types_path is deprecated and ignored; static parser patterns are used")
    results: list[tuple[list[NodeInfo], list[EdgeInfo]] | None] = [None] * len(source_files)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        future_to_idx = {
            executor.submit(_parse_one_file, fp): i
            for i, fp in enumerate(source_files)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to parse {source_files[idx]} in worker process"
                ) from exc
    return results  # type: ignore[return-value]


def _parse_one_file(file_path: Path) -> tuple[list[NodeInfo], list[EdgeInfo]]:
    """Parse a source file in a subprocess-safe top-level function."""
    try:
        from .parser import CodeParser
    except ImportError:  # script/installed-tools flat execution
        from parser import CodeParser

    parser = CodeParser()
    return parser.parse_file(file_path)


def _rule_search_dirs(repo_root: Path) -> list[Path]:
    """Directories to look for rule files in, project root first.

    Root-first ordering means a rule file nearer the analysis root wins. The
    walk stops at the first directory holding a `_ROOT_MARKERS` entry; if none
    is found the ancestors are discarded rather than read, so a p4 workspace or
    exported tree does not pull in unrelated `.gitignore` files up to `/`.
    """
    dirs = [repo_root]
    current = repo_root
    while current != current.parent:
        if any((current / marker).exists() for marker in _ROOT_MARKERS):
            return list(reversed(dirs))
        current = current.parent
        dirs.append(current)
    return [repo_root]


def _p4_ignore_names() -> tuple[str, ...]:
    """Rule file names p4 uses: ``P4IGNORE`` if set, else the platform defaults.

    ``P4IGNORE`` holds a semicolon-separated list of names or absolute paths.
    P4 Server set no default name before 2023.2, so real workspaces usually
    configure it explicitly and the defaults alone would miss their rules.
    """
    configured = os.environ.get("P4IGNORE", "").strip()
    if not configured:
        return _P4_IGNORE_FILES
    return tuple(name.strip() for name in configured.split(";") if name.strip())


def _ignore_rule_files(repo_root: Path) -> list[Path]:
    """Existing rule files in increasing precedence order.

    Absolute ``P4IGNORE`` entries are machine-wide rules, so they come first
    (lowest precedence) and repository-local files override them.
    """
    names = (_GIT_IGNORE_FILE, *_p4_ignore_names(), _CODE2SPEC_IGNORE_FILE)
    candidates = [Path(name) for name in names if os.path.isabs(name)]
    candidates += [
        base / name
        for base in _rule_search_dirs(repo_root)
        for name in names
        if not os.path.isabs(name)
    ]
    return [path for path in candidates if path.is_file()]


def _parse_ignore_rules(path: Path) -> list[tuple[str, bool]]:
    """Parse one rule file into ordered ``(directory_name, negated)`` pairs.

    `.gitignore`, `.p4ignore` and `.code2specignore` share this syntax. Only
    single-segment directory names are supported, because the caller matches by
    path segment; multi-segment paths (``a/b``) and globs (``*.log``) can't be
    applied to a single segment. Those lines are dropped with a warning rather
    than silently, so a rule that cannot take effect stays visible.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []

    rules: list[tuple[str, bool]] = []
    for raw in lines:
        entry = raw.strip()
        if not entry or entry.startswith("#"):
            continue
        negated = entry.startswith("!")
        if negated:
            entry = entry[1:].strip()
        # Normalize anchoring/directory markers: `/dist/` -> `dist`.
        entry = entry.strip("/")
        if not entry:
            continue
        if "/" in entry or any(ch in entry for ch in "*?[]"):
            logger.warning(
                "%s: unsupported pattern %r - only plain directory names are "
                "matched, so this line has no effect.",
                path,
                raw.strip(),
            )
            continue
        rules.append((entry, negated))
    return rules


def _resolve_ignore_dirs(repo_root: Path) -> set[str]:
    """Directory names to skip: the baseline with each rule file folded on top.

    Later rules win, matching git and p4 semantics, so `.code2specignore` has
    the final say and a repo can re-include a wrongly excluded directory. This
    lets ecosystem layout decide exclusion instead of a hardcoded list: where
    ``packages/`` is generated output it is ignored, while in a pnpm/yarn
    monorepo holding source it is tracked and kept. See issue #3.
    """
    ignore = set(_IGNORE_DIRS)
    for path in _ignore_rule_files(repo_root):
        for name, negated in _parse_ignore_rules(path):
            if negated:
                ignore.discard(name)
            else:
                ignore.add(name)
    return ignore


def _collect_source_files(repo_root: Path, min_lines: int = 0) -> list[Path]:
    """Collect all source files below the requested analysis root.

    Uses os.scandir for faster directory traversal than rglob.
    """
    repo_root = repo_root.resolve()
    files: list[Path] = []
    ignore_dirs = _resolve_ignore_dirs(repo_root)

    def _scan_dir(dir_path: Path) -> None:
        try:
            with os.scandir(dir_path) as entries:
                for entry in entries:
                    name = entry.name
                    # Skip hidden files/directories
                    if name.startswith("."):
                        continue
                    # Skip ignored directories
                    if entry.is_dir(follow_symlinks=False):
                        if name in ignore_dirs:
                            continue
                        _scan_dir(Path(entry.path))
                    elif entry.is_file(follow_symlinks=False):
                        # Check extension
                        ext = os.path.splitext(name)[1].lower()
                        if ext not in _SOURCE_EXTENSIONS:
                            continue
                        # Check file size
                        try:
                            stat = entry.stat(follow_symlinks=False)
                            if stat.st_size > 1_000_000:
                                continue
                            if min_lines > 0 and stat.st_size > 0:
                                # Quick line count check
                                with open(entry.path, "rb") as f:
                                    line_count = f.read().count(b"\n")
                                if line_count < min_lines:
                                    continue
                        except OSError:
                            continue
                        files.append(Path(entry.path))
        except OSError:
            pass

    _scan_dir(repo_root)
    return sorted(files)


def _collect_code_size(source_files: list[Path]) -> CodeSize:
    """Collect code size statistics from source files."""
    total_lines = 0
    total_bytes = 0
    by_extension: dict[str, dict[str, int]] = {}

    for file_path in source_files:
        try:
            content = file_path.read_bytes()
            line_count = content.count(b"\n") + 1
            byte_size = len(content)

            total_lines += line_count
            total_bytes += byte_size

            ext = file_path.suffix.lower()
            if ext not in by_extension:
                by_extension[ext] = {"files": 0, "lines": 0, "bytes": 0}
            by_extension[ext]["files"] += 1
            by_extension[ext]["lines"] += line_count
            by_extension[ext]["bytes"] += byte_size
        except OSError:
            continue

    return CodeSize(
        total_files=len(source_files),
        total_lines=total_lines,
        total_bytes=total_bytes,
        by_extension=by_extension,
    )


def get_code_size(repo_root: Path, min_lines: int = 0) -> CodeSize:
    """Get code size statistics without full AST parsing.

    This is a lightweight function for quickly getting code metrics.
    """
    source_files = _collect_source_files(repo_root, min_lines)
    return _collect_code_size(source_files)


# ── JSON export (dict-based, no object materialisation) ───────────────────────


def _export_json_dicts(
    node_dicts: list[dict],
    edge_dicts: list[dict],
    repo_root: Path,
    output_path: Path,
) -> None:
    """Export raw node/edge dicts as JSON (no NodeInfo/EdgeInfo conversion)."""
    data = {
        "metadata": {
            "generated_from": str(repo_root),
            "total_nodes": len(node_dicts),
            "total_edges": len(edge_dicts),
        },
        "nodes": node_dicts,
        "edges": edge_dicts,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _export_json(
    nodes: list[NodeInfo],
    edges: list[EdgeInfo],
    repo_root: Path,
    output_path: Path,
) -> None:
    """Export raw node/edge data as JSON for fast programmatic consumption."""
    data = {
        "metadata": {
            "generated_from": str(repo_root),
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        },
        "nodes": [n.to_dict() for n in nodes],
        "edges": [e.to_dict() for e in edges],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


# ── Raw Markdown export (dict-based) ──────────────────────────────────────────


def _export_raw_dicts(
    node_dicts: list[dict],
    edge_dicts: list[dict],
    repo_root: Path,
    output_path: Path,
) -> None:
    """Export raw node/edge dicts as Markdown tables (no object conversion)."""
    lines = [
        "# Code Graph - Raw Data",
        "",
        f"Generated from: `{repo_root}`",
        "",
        "## Nodes",
        "",
        "| Kind | Name | File | Lines | Parent |",
        "|------|------|------|-------|--------|",
    ]

    nodes_by_kind: dict[str, list[dict]] = {}
    for n in node_dicts:
        nodes_by_kind.setdefault(n.get("kind", ""), []).append(n)

    kind_order = ["File", "Class", "Function", "Type", "Test", "Enum", "Constant"]
    for kind in kind_order:
        if kind not in nodes_by_kind:
            continue
        for n in nodes_by_kind[kind]:
            rel_path = _relative_path(n.get("file_path", ""), repo_root)
            parent = n.get("parent_name") or "-"
            lines.append(
                f"| {n.get('kind', '')} | `{n.get('name', '')}` | `{rel_path}` | "
                f"{n.get('line_start', 0)}-{n.get('line_end', 0)} | {parent} |"
            )

    lines.extend(
        [
            "",
            "## Edges",
            "",
            "| Kind | Source | Target | File | Line |",
            "|------|--------|--------|------|------|",
        ]
    )

    edges_by_kind: dict[str, list[dict]] = {}
    for e in edge_dicts:
        edges_by_kind.setdefault(e.get("kind", ""), []).append(e)

    edge_order = [
        "CONTAINS",
        "CALLS",
        "IMPORTS_FROM",
        "INHERITS",
        "IMPLEMENTS",
        "TESTED_BY",
        "DEPENDS_ON",
    ]
    for kind in edge_order:
        if kind not in edges_by_kind:
            continue
        for e in edges_by_kind[kind]:
            rel_path = _relative_path(e.get("file_path", ""), repo_root)
            source = _shorten_name(e.get("source", ""), repo_root)
            target = _shorten_name(e.get("target", ""), repo_root)
            lines.append(
                f"| {e.get('kind', '')} | `{source}` | `{target}` | `{rel_path}` | {e.get('line', 0)} |"
            )

    # Enum Definitions section
    enum_nodes = nodes_by_kind.get("Enum", [])
    if enum_nodes:
        lines.extend(
            [
                "",
                "## Enum Definitions",
                "",
                "| Enum Name | File | Members (name=value) | Source |",
                "|-----------|------|----------------------|--------|",
            ]
        )
        for n in enum_nodes:
            rel_path = _relative_path(n.get("file_path", ""), repo_root)
            extra = n.get("extra", {})
            values = extra.get("values", {})
            values_str = ", ".join(f"{k}={v}" for k, v in values.items()) if values else "N/A"
            lines.append(
                f"| `{n.get('name', '')}` | `{rel_path}` | {values_str} | :L{n.get('line_start', 0)}-L{n.get('line_end', 0)} |"
            )

    # IPC Connections section
    ipc_edges = edges_by_kind.get("IPC", [])
    if ipc_edges:
        lines.extend(
            [
                "",
                "## IPC Connections",
                "",
                "| Source | Target | Mechanism | Direction | File | Line |",
                "|--------|--------|-----------|-----------|------|------|",
            ]
        )
        for e in ipc_edges:
            rel_path = _relative_path(e.get("file_path", ""), repo_root)
            extra = e.get("extra", {})
            mechanism = extra.get("ipc_mechanism", "unknown")
            direction = extra.get("direction", "unknown")
            lines.append(
                f"| `{_shorten_name(e.get('source', ''), repo_root)}` | `{_shorten_name(e.get('target', ''), repo_root)}` | {mechanism} | {direction} | `{rel_path}` | {e.get('line', 0)} |"
            )

    # Constant Definitions section
    constant_nodes = nodes_by_kind.get("Constant", [])
    if constant_nodes:
        lines.extend(
            [
                "",
                "## Constant Definitions",
                "",
                "| Name | Value | File | Lines | Parent |",
                "|------|-------|------|-------|--------|",
            ]
        )
        for n in constant_nodes:
            rel_path = _relative_path(n.get("file_path", ""), repo_root)
            parent = n.get("parent_name") or "-"
            extra = n.get("extra", {})
            value = extra.get("value", "N/A")
            lines.append(
                f"| `{n.get('name', '')}` | {value} | `{rel_path}` | "
                f"{n.get('line_start', 0)}-{n.get('line_end', 0)} | {parent} |"
            )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- **Total Nodes**: {len(node_dicts)}",
            f"- **Total Edges**: {len(edge_dicts)}",
            "",
            "### Nodes by Kind",
            "",
        ]
    )
    for kind, node_list in sorted(nodes_by_kind.items()):
        lines.append(f"- {kind}: {len(node_list)}")

    lines.extend(
        [
            "",
            "### Edges by Kind",
            "",
        ]
    )
    for kind, edge_list in sorted(edges_by_kind.items()):
        lines.append(f"- {kind}: {len(edge_list)}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _export_raw(
    nodes: list[NodeInfo],
    edges: list[EdgeInfo],
    repo_root: Path,
    output_path: Path,
) -> None:
    """Export raw node/edge data as Markdown tables."""
    lines = [
        "# Code Graph - Raw Data",
        "",
        f"Generated from: `{repo_root}`",
        "",
        "## Nodes",
        "",
        "| Kind | Name | File | Lines | Parent |",
        "|------|------|------|-------|--------|",
    ]

    nodes_by_kind: dict[str, list[NodeInfo]] = {}
    for node in nodes:
        nodes_by_kind.setdefault(node.kind, []).append(node)

    kind_order = ["File", "Class", "Function", "Type", "Test", "Enum", "Constant"]
    for kind in kind_order:
        if kind not in nodes_by_kind:
            continue
        for node in nodes_by_kind[kind]:
            rel_path = _relative_path(node.file_path, repo_root)
            parent = node.parent_name or "-"
            lines.append(
                f"| {node.kind} | `{node.name}` | `{rel_path}` | "
                f"{node.line_start}-{node.line_end} | {parent} |"
            )

    lines.extend(
        [
            "",
            "## Edges",
            "",
            "| Kind | Source | Target | File | Line |",
            "|------|--------|--------|------|------|",
        ]
    )

    edges_by_kind: dict[str, list[EdgeInfo]] = {}
    for edge in edges:
        edges_by_kind.setdefault(edge.kind, []).append(edge)

    edge_order = [
        "CONTAINS",
        "CALLS",
        "IMPORTS_FROM",
        "INHERITS",
        "IMPLEMENTS",
        "TESTED_BY",
        "DEPENDS_ON",
    ]
    for kind in edge_order:
        if kind not in edges_by_kind:
            continue
        for edge in edges_by_kind[kind]:
            rel_path = _relative_path(edge.file_path, repo_root)
            source = _shorten_name(edge.source, repo_root)
            target = _shorten_name(edge.target, repo_root)
            lines.append(
                f"| {edge.kind} | `{source}` | `{target}` | `{rel_path}` | {edge.line} |"
            )

    # Enum Definitions section - surface enum values from parser's extra["values"]
    enum_nodes = nodes_by_kind.get("Enum", [])
    if enum_nodes:
        lines.extend(
            [
                "",
                "## Enum Definitions",
                "",
                "| Enum Name | File | Members (name=value) | Source |",
                "|-----------|------|----------------------|--------|",
            ]
        )
        for node in enum_nodes:
            rel_path = _relative_path(node.file_path, repo_root)
            values = node.extra.get("values", {})
            values_str = ", ".join(f"{k}={v}" for k, v in values.items()) if values else "N/A"
            lines.append(
                f"| `{node.name}` | `{rel_path}` | {values_str} | :L{node.line_start}-L{node.line_end} |"
            )

    # IPC Connections section - surface IPC mechanism from parser's extra["ipc_mechanism"]
    ipc_edges = edges_by_kind.get("IPC", [])
    if ipc_edges:
        lines.extend(
            [
                "",
                "## IPC Connections",
                "",
                "| Source | Target | Mechanism | Direction | File | Line |",
                "|--------|--------|-----------|-----------|------|------|",
            ]
        )
        for edge in ipc_edges:
            rel_path = _relative_path(edge.file_path, repo_root)
            mechanism = edge.extra.get("ipc_mechanism", "unknown")
            direction = edge.extra.get("direction", "unknown")
            lines.append(
                f"| `{_shorten_name(edge.source, repo_root)}` | `{_shorten_name(edge.target, repo_root)}` | {mechanism} | {direction} | `{rel_path}` | {edge.line} |"
            )

    # Constant Definitions section - surface constants from parser's extra["value"]
    constant_nodes = nodes_by_kind.get("Constant", [])
    if constant_nodes:
        lines.extend(
            [
                "",
                "## Constant Definitions",
                "",
                "| Name | Value | File | Lines | Parent |",
                "|------|-------|------|-------|--------|",
            ]
        )
        for node in constant_nodes:
            rel_path = _relative_path(node.file_path, repo_root)
            parent = node.parent_name or "-"
            value = node.extra.get("value", "N/A")
            lines.append(
                f"| `{node.name}` | {value} | `{rel_path}` | "
                f"{node.line_start}-{node.line_end} | {parent} |"
            )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- **Total Nodes**: {len(nodes)}",
            f"- **Total Edges**: {len(edges)}",
            "",
            "### Nodes by Kind",
            "",
        ]
    )
    for kind, node_list in sorted(nodes_by_kind.items()):
        lines.append(f"- {kind}: {len(node_list)}")

    lines.extend(
        [
            "",
            "### Edges by Kind",
            "",
        ]
    )
    for kind, edge_list in sorted(edges_by_kind.items()):
        lines.append(f"- {kind}: {len(edge_list)}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── Core selection (dict-based, no object conversion) ─────────────────────────


def _select_core_modules_from_dicts(
    node_dicts: list[dict],
    edge_dicts: list[dict],
    repo_root: Path,
) -> list[str]:
    """메모리에서 바로 PageRank Core 모듈 선정 (dict 기반, 객체 변환 없음).

    ast_analyzer.py를 파일 I/O 없이 직접 호출하여 Core 파일 목록만 반환.
    실패 시 빈 리스트 반환 (Mermaid 전체 생성 fallback).
    """
    try:
        try:
            from .ast_analyzer import (
                CentralityConfig,
                classify_files_by_centrality,
                compute_in_degree,
                find_entry_points,
            )
        except ImportError:  # script/installed-tools flat execution
            from ast_analyzer import (
                CentralityConfig,
                classify_files_by_centrality,
                compute_in_degree,
                find_entry_points,
            )

        # dict를 ast_analyzer 호환 형식으로 직접 변환 (NodeInfo 객체 생성 없음)
        dict_nodes = [
            {
                "kind": n.get("kind", ""),
                "name": n.get("name", ""),
                "file": n.get("file_path", ""),
                "lines": f"{n.get('line_start', 0)}-{n.get('line_end', 0)}",
                "parent": n.get("parent_name"),
            }
            for n in node_dicts
        ]
        dict_edges = [
            {
                "kind": e.get("kind", ""),
                "source": e.get("source", ""),
                "target": e.get("target", ""),
                "file": e.get("file_path", ""),
                "line": str(e.get("line", 0)),
            }
            for e in edge_dicts
        ]

        # Entry points 탐지
        in_degree = compute_in_degree(dict_nodes, dict_edges)
        entry_points = find_entry_points(in_degree, dict_nodes)

        # PageRank Core 선정
        config = CentralityConfig()
        core, peripheral, method = classify_files_by_centrality(
            dict_nodes,
            dict_edges,
            entry_points,
            z_multiplier=1.0,
            max_core=20,
            repo_root=str(repo_root),
            centrality_config=config,
        )

        core_files = [item["file"] for item in core]
        print(
            f"[Export] Core modules selected in-memory: {len(core_files)} files "
            f"(method={method})"
        )
        return core_files

    except Exception as e:
        print(f"[Export] ⚠ In-memory core selection failed: {e}")
        return []


def _select_core_modules_in_memory(
    nodes: list[NodeInfo],
    edges: list[EdgeInfo],
    repo_root: Path,
) -> list[str]:
    """메모리에서 바로 PageRank Core 모듈 선정 (옵션 C 파이프라인).

    ast_analyzer.py를 파일 I/O 없이 직접 호출하여 Core 파일 목록만 반환.
    실패 시 빈 리스트 반환 (Mermaid 전체 생성 fallback).

    Returns:
        Core 파일 경로 리스트 (상대경로)
    """
    try:
        try:
            from .ast_analyzer import (
                CentralityConfig,
                classify_files_by_centrality,
                compute_in_degree,
                find_entry_points,
            )
        except ImportError:  # script/installed-tools flat execution
            from ast_analyzer import (
                CentralityConfig,
                classify_files_by_centrality,
                compute_in_degree,
                find_entry_points,
            )

        # NodeInfo → ast_analyzer 호환 dict로 변환
        # ast_analyzer는 "file", "lines", "parent" 키 사용 (to_dict()와 다름)
        dict_nodes = [
            {
                "kind": n.kind,
                "name": n.name,
                "file": n.file_path,
                "lines": f"{n.line_start}-{n.line_end}",
                "parent": n.parent_name,
            }
            for n in nodes
        ]
        dict_edges = [
            {
                "kind": e.kind,
                "source": e.source,
                "target": e.target,
                "file": e.file_path,
                "line": str(e.line),
            }
            for e in edges
        ]

        # Entry points 탐지
        in_degree = compute_in_degree(dict_nodes, dict_edges)
        entry_points = find_entry_points(in_degree, dict_nodes)

        # PageRank Core 선정
        config = CentralityConfig()
        core, peripheral, method = classify_files_by_centrality(
            dict_nodes,
            dict_edges,
            entry_points,
            z_multiplier=1.0,
            max_core=20,
            repo_root=str(repo_root),
            centrality_config=config,
        )

        core_files = [item["file"] for item in core]
        print(
            f"[Export] Core modules selected in-memory: {len(core_files)} files "
            f"(method={method})"
        )
        return core_files

    except Exception as e:
        print(f"[Export] ⚠ In-memory core selection failed: {e}")
        return []


# ── Mermaid export (dict-based, reverse-index optimised) ──────────────────────


def _build_file_reverse_index(
    file_paths: list[str], repo_root: Path
) -> dict[str, str]:
    """Build a reverse index: target_suffix → file_path for O(1) lookup.

    Maps both the full relative path and the basename to the file path,
    so import targets can be resolved without O(N) linear scans.
    """
    index: dict[str, str] = {}
    for fp in file_paths:
        # Full path
        index[fp] = fp
        # Relative path
        rel = _relative_path(fp, repo_root)
        index[rel] = fp
        # Basename
        basename = os.path.basename(fp)
        index[basename] = fp
        # Stem (filename without extension)
        stem = os.path.splitext(basename)[0]
        if stem not in index:
            index[stem] = fp
    return index


def _export_mermaid_core_dicts(
    node_dicts: list[dict],
    edge_dicts: list[dict],
    core_files: list[str],
    repo_root: Path,
    output_dir: Path,
    max_nodes: int = 500,
) -> list[str]:
    """Core 모듈 + 직접 의존 모듈만 Mermaid 다이어그램 생성 (dict 기반, 역색인).

    전체 프로젝트 대신 Core 모듈과 그 직접 의존 모듈만 포함하여
    다이어그램 크기를 대폭 줄임.
    """
    output_files = []

    # Core 파일 집합 + 직접 의존 파일 집합 구성 (역색인, O(edges))
    core_set = set(core_files)
    related_files = set(core_files)

    # Build reverse index for target resolution
    all_file_paths = {n.get("file_path", "") for n in node_dicts if n.get("kind") == "File"}
    target_index = _build_file_reverse_index(list(all_file_paths), repo_root)

    for edge in edge_dicts:
        kind = edge.get("kind", "")
        if kind in ("IMPORTS_FROM", "CALLS"):
            src_file = edge.get("file_path", "")
            if src_file in core_set:
                related_files.add(src_file)
            # Check if target resolves to a core file (O(1) via set)
            target = edge.get("target", "")
            if target in core_set:
                related_files.add(src_file)
            # Also check via reverse index
            resolved = target_index.get(target)
            if resolved and resolved in core_set:
                related_files.add(src_file)

    # 필터링된 노드/엣지
    filtered_nodes = [n for n in node_dicts if n.get("file_path", "") in related_files]
    filtered_edges = [
        e for e in edge_dicts
        if e.get("kind", "") in ("IMPORTS_FROM", "CALLS", "INHERITS", "IMPLEMENTS")
        and e.get("file_path", "") in related_files
    ]

    print(
        f"[Export] Mermaid core: {len(filtered_nodes)} nodes, "
        f"{len(filtered_edges)} edges (from {len(node_dicts)} total nodes)"
    )

    # 노드를 kind별로 분류
    file_nodes = [n for n in filtered_nodes if n.get("kind") == "File"]
    class_nodes = [n for n in filtered_nodes if n.get("kind") == "Class"]
    func_nodes = [n for n in filtered_nodes if n.get("kind") in ("Function", "Test")]

    edges_by_kind: dict[str, list[dict]] = defaultdict(list)
    for edge in filtered_edges:
        edges_by_kind[edge.get("kind", "")].append(edge)

    # 1. Core summary diagram
    summary_path = output_dir / "00-core-summary.md"
    _export_core_summary_diagram_dicts(
        file_nodes,
        edges_by_kind.get("IMPORTS_FROM", []),
        core_set,
        repo_root,
        summary_path,
    )
    output_files.append(str(summary_path))

    # 2. Core CALLS diagram
    calls_path = output_dir / "01-core-calls.md"
    _export_calls_diagram_dicts(
        class_nodes,
        func_nodes,
        edges_by_kind.get("CALLS", []),
        repo_root,
        calls_path,
        max_nodes,
    )
    output_files.append(str(calls_path))

    # 3. Core inheritance (있는 경우만)
    inherits_edges = edges_by_kind.get("INHERITS", []) + edges_by_kind.get(
        "IMPLEMENTS", []
    )
    if inherits_edges:
        inherits_path = output_dir / "02-core-inherits.md"
        _export_inherits_diagram_dicts(class_nodes, inherits_edges, repo_root, inherits_path)
        output_files.append(str(inherits_path))

    return output_files


def _export_core_summary_diagram_dicts(
    file_nodes: list[dict],
    import_edges: list[dict],
    core_set: set[str],
    repo_root: Path,
    output_path: Path,
) -> None:
    """Core 모듈 요약 다이어그램 (Core는 빨간색 스타일, 역색인 O(1) 조회)."""
    lines = [
        "# Code Graph - Core Module Summary",
        "",
        f"Generated from: `{repo_root}`",
        f"Core modules: {len(core_set)}",
        "",
        "```mermaid",
        "graph TD",
    ]

    file_ids: dict[str, str] = {}
    for i, node in enumerate(file_nodes):
        fp = node.get("file_path", "")
        rel_path = _relative_path(fp, repo_root)
        node_id = f"f{i}"
        file_ids[fp] = node_id
        lines.append(f'    {node_id}["{rel_path}"]')
        # Core 모듈은 빨간색 스타일
        if fp in core_set:
            lines.append(f"    style {node_id} fill:#f96,stroke:#333,color:#fff")

    # Build reverse index for target resolution (O(1) lookup)
    target_index = _build_file_reverse_index(list(file_ids.keys()), repo_root)

    seen_imports = set()
    for edge in import_edges:
        source_file = edge.get("file_path", "")
        target = edge.get("target", "")
        # O(1) lookup via reverse index
        target_file = target_index.get(target)
        if not target_file:
            # Try suffix matching via index
            for fp in file_ids:
                if target in fp or fp.endswith(target):
                    target_file = fp
                    break

        if source_file in file_ids and target_file and target_file in file_ids:
            key = (source_file, target_file)
            if key not in seen_imports:
                seen_imports.add(key)
                lines.append(
                    f"    {file_ids[source_file]} -->|imports| {file_ids[target_file]}"
                )

    lines.extend(
        [
            "```",
            "",
            "## Legend",
            "",
            "- 🔴 **Red background** = Core module",
            "- Default background = Related module",
            f"- **Total Files**: {len(file_nodes)}",
            f"- **Import Relationships**: {len(seen_imports)}",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _export_mermaid_all_dicts(
    node_dicts: list[dict],
    edge_dicts: list[dict],
    repo_root: Path,
    output_dir: Path,
    max_nodes: int = 500,
) -> list[str]:
    """Export multiple Mermaid diagram files with full information (dict-based)."""
    output_files = []

    file_nodes = [n for n in node_dicts if n.get("kind") == "File"]
    class_nodes = [n for n in node_dicts if n.get("kind") == "Class"]
    func_nodes = [n for n in node_dicts if n.get("kind") in ("Function", "Test")]

    edges_by_kind: dict[str, list[dict]] = defaultdict(list)
    for edge in edge_dicts:
        edges_by_kind[edge.get("kind", "")].append(edge)

    # 1. Summary diagram
    summary_path = output_dir / "00-summary.md"
    _export_summary_diagram_dicts(
        file_nodes, edges_by_kind.get("IMPORTS_FROM", []), repo_root, summary_path
    )
    output_files.append(str(summary_path))

    # 2. All CALLS relationships
    calls_path = output_dir / "01-calls-all.md"
    _export_calls_diagram_dicts(
        class_nodes,
        func_nodes,
        edges_by_kind.get("CALLS", []),
        repo_root,
        calls_path,
        max_nodes,
    )
    output_files.append(str(calls_path))

    # 3. Inheritance relationships
    inherits_edges = edges_by_kind.get("INHERITS", []) + edges_by_kind.get(
        "IMPLEMENTS", []
    )
    if inherits_edges:
        inherits_path = output_dir / "02-inherits.md"
        _export_inherits_diagram_dicts(class_nodes, inherits_edges, repo_root, inherits_path)
        output_files.append(str(inherits_path))

    # 4. Test relationships
    test_edges = edges_by_kind.get("TESTED_BY", [])
    if test_edges:
        tests_path = output_dir / "03-tests.md"
        _export_tests_diagram_dicts(func_nodes, test_edges, repo_root, tests_path)
        output_files.append(str(tests_path))

    # 5. Module-level diagrams
    by_module_dir = output_dir / "by-module"
    by_module_dir.mkdir(parents=True, exist_ok=True)
    module_files = _export_by_module_dicts(
        class_nodes, func_nodes, edges_by_kind, repo_root, by_module_dir, max_nodes
    )
    output_files.extend(module_files)

    return output_files


def _export_summary_diagram_dicts(
    file_nodes: list[dict],
    import_edges: list[dict],
    repo_root: Path,
    output_path: Path,
) -> None:
    """Export file-level summary diagram (dict-based, reverse-index O(1) lookup)."""
    lines = [
        "# Code Graph - Summary (File Level)",
        "",
        f"Generated from: `{repo_root}`",
        "",
        "```mermaid",
        "graph TD",
    ]

    file_ids: dict[str, str] = {}
    for i, node in enumerate(file_nodes):
        fp = node.get("file_path", "")
        rel_path = _relative_path(fp, repo_root)
        node_id = f"f{i}"
        file_ids[fp] = node_id
        lines.append(f'    {node_id}["{rel_path}"]')

    # Build reverse index for O(1) target resolution
    target_index = _build_file_reverse_index(list(file_ids.keys()), repo_root)

    seen_imports = set()
    for edge in import_edges:
        source_file = edge.get("file_path", "")
        target = edge.get("target", "")
        # O(1) lookup via reverse index
        target_file = target_index.get(target)
        if not target_file:
            # Fallback: suffix matching
            for fp in file_ids:
                if target in fp or fp.endswith(target):
                    target_file = fp
                    break

        if source_file in file_ids and target_file and target_file in file_ids:
            key = (source_file, target_file)
            if key not in seen_imports:
                seen_imports.add(key)
                lines.append(
                    f"    {file_ids[source_file]} -->|imports| {file_ids[target_file]}"
                )

    lines.extend(
        [
            "```",
            "",
            f"**Total Files**: {len(file_nodes)}",
            f"**Import Relationships**: {len(seen_imports)}",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _export_calls_diagram_dicts(
    class_nodes: list[dict],
    func_nodes: list[dict],
    call_edges: list[dict],
    repo_root: Path,
    output_path: Path,
    max_nodes: int,
) -> None:
    """Export all CALLS relationships as Mermaid diagrams (dict-based)."""
    lines = [
        "# Code Graph - All Function Calls",
        "",
        f"Generated from: `{repo_root}`",
        "",
        f"Total call relationships: {len(call_edges)}",
        "",
    ]

    nodes_by_file: dict[str, list[dict]] = defaultdict(list)
    for n in class_nodes + func_nodes:
        nodes_by_file[n.get("file_path", "")].append(n)

    if len(nodes_by_file) > 15 or len(call_edges) > 500:
        lines.append("## Diagrams by Module")
        lines.append("")

        modules = defaultdict(lambda: defaultdict(list))
        for file_path, file_nodes_list in nodes_by_file.items():
            rel_path = _relative_path(file_path, repo_root)
            module = rel_path.split("/")[0] if "/" in rel_path else "root"
            modules[module][file_path] = file_nodes_list

        for module_name, module_files in sorted(modules.items()):
            module_nodes = []
            for file_nodes_list in module_files.values():
                module_nodes.extend(file_nodes_list)

            module_qnames = {_qualify_dict(n) for n in module_nodes}
            module_edges = [
                e
                for e in call_edges
                if e.get("source", "") in module_qnames or e.get("target", "") in module_qnames
            ]

            if module_nodes:
                lines.append(f"### Module: {module_name}")
                lines.append("")
                lines.append("```mermaid")
                lines.append("graph TD")

                node_ids: dict[str, str] = {}
                counter = [0]

                def get_id(
                    qname: str, _node_ids: dict = node_ids, _counter: list = counter
                ) -> str:
                    if qname not in _node_ids:
                        _node_ids[qname] = f"n{_counter[0]}"
                        _counter[0] += 1
                    return _node_ids[qname]

                for n in module_nodes[:max_nodes]:
                    qname = _qualify_dict(n)
                    node_id = get_id(qname)
                    kind = n.get("kind", "")
                    name = n.get("name", "")
                    if kind == "Class":
                        lines.append(f'    {node_id}[["{name}"]]')
                    elif kind == "Test":
                        lines.append(f'    {node_id}("{name}")')
                    else:
                        lines.append(f'    {node_id}["{name}"]')

                seen = set()
                for edge in module_edges[:500]:
                    source_id = get_id(edge.get("source", ""))
                    target_id = get_id(edge.get("target", ""))
                    key = (edge.get("source", ""), edge.get("target", ""))
                    if key not in seen:
                        seen.add(key)
                        lines.append(f"    {source_id} -->|calls| {target_id}")

                lines.append("```")
                lines.append("")
    else:
        lines.append("```mermaid")
        lines.append("graph TD")

        node_ids: dict[str, str] = {}
        counter = [0]

        def get_id(qname: str) -> str:
            if qname not in node_ids:
                node_ids[qname] = f"n{counter[0]}"
                counter[0] += 1
            return node_ids[qname]

        for file_path, file_nodes_list in sorted(nodes_by_file.items()):
            rel_path = _relative_path(file_path, repo_root)
            subgraph_id = rel_path.replace("/", "_").replace(".", "_").replace("-", "_")
            lines.append(f'    subgraph {subgraph_id}["{rel_path}"]')

            for n in file_nodes_list:
                qname = _qualify_dict(n)
                node_id = get_id(qname)
                kind = n.get("kind", "")
                name = n.get("name", "")
                if kind == "Class":
                    lines.append(f'        {node_id}[["{name}"]]')
                elif kind == "Test":
                    lines.append(f'        {node_id}("{name}")')
                else:
                    lines.append(f'        {node_id}["{name}"]')

            lines.append("    end")

        seen = set()
        for edge in call_edges:
            source_id = get_id(edge.get("source", ""))
            target_id = get_id(edge.get("target", ""))
            key = (edge.get("source", ""), edge.get("target", ""))
            if key not in seen:
                seen.add(key)
                lines.append(f"    {source_id} -->|calls| {target_id}")

        lines.append("```")
        lines.extend(
            [
                "",
                "## Legend",
                "",
                "- `[[Class]]` - Class nodes",
                "- `[Function]` - Function nodes",
                "- `(Test)` - Test nodes",
                "- `-->` - Calls relationship",
            ]
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _export_inherits_diagram_dicts(
    class_nodes: list[dict],
    inherits_edges: list[dict],
    repo_root: Path,
    output_path: Path,
) -> None:
    """Export inheritance hierarchy as Mermaid diagram (dict-based)."""
    lines = [
        "# Code Graph - Inheritance Hierarchy",
        "",
        f"Generated from: `{repo_root}`",
        "",
        f"Total inheritance relationships: {len(inherits_edges)}",
        "",
        "```mermaid",
        "graph TD",
    ]

    node_ids: dict[str, str] = {}
    counter = [0]

    def get_id(name: str) -> str:
        if name not in node_ids:
            node_ids[name] = f"c{counter[0]}"
            counter[0] += 1
        return node_ids[name]

    for n in class_nodes:
        qname = _qualify_dict(n)
        node_id = get_id(qname)
        lines.append(f'    {node_id}[["{n.get("name", "")}"]]')

    for edge in inherits_edges:
        source_id = get_id(edge.get("source", ""))
        target_id = get_id(edge.get("target", ""))
        label = "extends" if edge.get("kind") == "INHERITS" else "implements"
        lines.append(f"    {source_id} -->|{label}| {target_id}")

    lines.extend(
        [
            "```",
            "",
            "## Legend",
            "",
            "- `[[Class]]` - Class nodes",
            "- `-->|extends|` - Inheritance",
            "- `-->|implements|` - Interface implementation",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _export_tests_diagram_dicts(
    func_nodes: list[dict],
    test_edges: list[dict],
    repo_root: Path,
    output_path: Path,
) -> None:
    """Export test relationships as Mermaid diagram (dict-based)."""
    lines = [
        "# Code Graph - Test Coverage",
        "",
        f"Generated from: `{repo_root}`",
        "",
        f"Total test relationships: {len(test_edges)}",
        "",
        "```mermaid",
        "graph LR",
    ]

    node_ids: dict[str, str] = {}
    counter = [0]

    def get_id(name: str) -> str:
        if name not in node_ids:
            node_ids[name] = f"t{counter[0]}"
            counter[0] += 1
        return node_ids[name]

    test_funcs = {e.get("target", "") for e in test_edges}
    prod_funcs = {e.get("source", "") for e in test_edges}

    for func_name in prod_funcs:
        node_id = get_id(func_name)
        short_name = func_name.split("::")[-1]
        lines.append(f'    {node_id}["{short_name}"]')

    for func_name in test_funcs:
        node_id = get_id(func_name)
        short_name = func_name.split("::")[-1]
        lines.append(f'    {node_id}("{short_name}")')

    for edge in test_edges:
        source_id = get_id(edge.get("source", ""))
        target_id = get_id(edge.get("target", ""))
        lines.append(f"    {source_id} -->|tested by| {target_id}")

    lines.extend(
        [
            "```",
            "",
            "## Legend",
            "",
            "- `[Function]` - Production code",
            "- `(Test)` - Test function",
            "- `-->|tested by|` - Test relationship",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _export_by_module_dicts(
    class_nodes: list[dict],
    func_nodes: list[dict],
    edges_by_kind: dict[str, list[dict]],
    repo_root: Path,
    output_dir: Path,
    max_nodes: int,
) -> list[str]:
    """Export detailed diagrams by module/directory (dict-based)."""
    output_files = []

    modules: dict[str, dict] = defaultdict(lambda: {"classes": [], "functions": []})

    for n in class_nodes:
        rel_path = _relative_path(n.get("file_path", ""), repo_root)
        module = rel_path.split("/")[0] if "/" in rel_path else "root"
        modules[module]["classes"].append(n)

    for n in func_nodes:
        rel_path = _relative_path(n.get("file_path", ""), repo_root)
        module = rel_path.split("/")[0] if "/" in rel_path else "root"
        modules[module]["functions"].append(n)

    all_call_edges = edges_by_kind.get("CALLS", [])
    all_inherits_edges = edges_by_kind.get("INHERITS", []) + edges_by_kind.get(
        "IMPLEMENTS", []
    )

    for module_name, module_data in sorted(modules.items()):
        if not module_data["classes"] and not module_data["functions"]:
            continue

        output_path = output_dir / f"{module_name.replace('/', '_')}.md"

        lines = [
            f"# Module: {module_name}",
            "",
            f"Generated from: `{repo_root}`",
            "",
        ]

        module_qnames = set()
        for n in module_data["classes"] + module_data["functions"]:
            module_qnames.add(_qualify_dict(n))

        module_calls = [
            e
            for e in all_call_edges
            if e.get("source", "") in module_qnames or e.get("target", "") in module_qnames
        ]
        module_inherits = [
            e
            for e in all_inherits_edges
            if e.get("source", "") in module_qnames or e.get("target", "") in module_qnames
        ]

        lines.append(f"- Classes: {len(module_data['classes'])}")
        lines.append(f"- Functions: {len(module_data['functions'])}")
        lines.append(f"- Call relationships: {len(module_calls)}")
        lines.append(f"- Inheritance relationships: {len(module_inherits)}")
        lines.append("")

        lines.append("```mermaid")
        lines.append("graph TD")

        node_ids: dict[str, str] = {}
        counter = [0]

        def get_id(
            qname: str, _node_ids: dict = node_ids, _counter: list = counter
        ) -> str:
            if qname not in _node_ids:
                _node_ids[qname] = f"n{_counter[0]}"
                _counter[0] += 1
            return _node_ids[qname]

        for n in module_data["classes"][:max_nodes]:
            qname = _qualify_dict(n)
            node_id = get_id(qname)
            lines.append(f'    {node_id}[["{n.get("name", "")}"]]')

        for n in module_data["functions"][:max_nodes]:
            qname = _qualify_dict(n)
            node_id = get_id(qname)
            if n.get("kind") == "Test":
                lines.append(f'    {node_id}("{n.get("name", "")}")')
            else:
                lines.append(f'    {node_id}["{n.get("name", "")}"]')

        seen = set()
        for edge in module_calls[:300]:
            source_id = get_id(edge.get("source", ""))
            target_id = get_id(edge.get("target", ""))
            key = (edge.get("source", ""), edge.get("target", ""))
            if key not in seen:
                seen.add(key)
                lines.append(f"    {source_id} -->|calls| {target_id}")

        for edge in module_inherits[:100]:
            source_id = get_id(edge.get("source", ""))
            target_id = get_id(edge.get("target", ""))
            label = "extends" if edge.get("kind") == "INHERITS" else "implements"
            lines.append(f"    {source_id} -->|{label}| {target_id}")

        lines.append("```")

        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        output_files.append(str(output_path))

    return output_files


# ── Legacy NodeInfo/EdgeInfo-based Mermaid functions (kept for backward compat) ─


def _export_mermaid_core(
    nodes: list[NodeInfo],
    edges: list[EdgeInfo],
    core_files: list[str],
    repo_root: Path,
    output_dir: Path,
    max_nodes: int = 500,
) -> list[str]:
    """Core 모듈 + 직접 의존 모듈만 Mermaid 다이어그램 생성."""
    output_files = []

    core_set = set(core_files)
    related_files = set(core_files)

    # IMPORTS_FROM/CALLS로 Core와 직접 연결된 파일 추가
    for edge in edges:
        if edge.kind in ("IMPORTS_FROM", "CALLS"):
            if edge.file_path in core_set:
                related_files.add(edge.file_path)
            for cf in core_set:
                if cf in edge.target or edge.target.endswith(cf):
                    related_files.add(edge.file_path)

    filtered_nodes = [n for n in nodes if n.file_path in related_files]
    filtered_edges = [
        e for e in edges
        if e.kind in ("IMPORTS_FROM", "CALLS", "INHERITS", "IMPLEMENTS")
        and e.file_path in related_files
    ]

    print(
        f"[Export] Mermaid core: {len(filtered_nodes)} nodes, "
        f"{len(filtered_edges)} edges (from {len(nodes)} total nodes)"
    )

    file_nodes = [n for n in filtered_nodes if n.kind == "File"]
    class_nodes = [n for n in filtered_nodes if n.kind == "Class"]
    func_nodes = [n for n in filtered_nodes if n.kind in ("Function", "Test")]

    edges_by_kind: dict[str, list[EdgeInfo]] = defaultdict(list)
    for edge in filtered_edges:
        edges_by_kind[edge.kind].append(edge)

    summary_path = output_dir / "00-core-summary.md"
    _export_core_summary_diagram(
        file_nodes,
        edges_by_kind.get("IMPORTS_FROM", []),
        core_set,
        repo_root,
        summary_path,
    )
    output_files.append(str(summary_path))

    calls_path = output_dir / "01-core-calls.md"
    _export_calls_diagram(
        class_nodes,
        func_nodes,
        edges_by_kind.get("CALLS", []),
        repo_root,
        calls_path,
        max_nodes,
    )
    output_files.append(str(calls_path))

    inherits_edges = edges_by_kind.get("INHERITS", []) + edges_by_kind.get(
        "IMPLEMENTS", []
    )
    if inherits_edges:
        inherits_path = output_dir / "02-core-inherits.md"
        _export_inherits_diagram(class_nodes, inherits_edges, repo_root, inherits_path)
        output_files.append(str(inherits_path))

    return output_files


def _export_core_summary_diagram(
    file_nodes: list[NodeInfo],
    import_edges: list[EdgeInfo],
    core_set: set[str],
    repo_root: Path,
    output_path: Path,
) -> None:
    """Core 모듈 요약 다이어그램 (Core는 빨간색 스타일)."""
    lines = [
        "# Code Graph - Core Module Summary",
        "",
        f"Generated from: `{repo_root}`",
        f"Core modules: {len(core_set)}",
        "",
        "```mermaid",
        "graph TD",
    ]

    file_ids: dict[str, str] = {}
    for i, node in enumerate(file_nodes):
        rel_path = _relative_path(node.file_path, repo_root)
        node_id = f"f{i}"
        file_ids[node.file_path] = node_id
        lines.append(f'    {node_id}["{rel_path}"]')
        if node.file_path in core_set:
            lines.append(f"    style {node_id} fill:#f96,stroke:#333,color:#fff")

    seen_imports = set()
    for edge in import_edges:
        source_file = edge.file_path
        target = edge.target
        target_file = None
        for fp in file_ids:
            if (
                target in fp
                or fp.endswith(target)
                or target.endswith(_relative_path(fp, repo_root))
            ):
                target_file = fp
                break

        if source_file in file_ids and target_file and target_file in file_ids:
            key = (source_file, target_file)
            if key not in seen_imports:
                seen_imports.add(key)
                lines.append(
                    f"    {file_ids[source_file]} -->|imports| {file_ids[target_file]}"
                )

    lines.extend(
        [
            "```",
            "",
            "## Legend",
            "",
            "- 🔴 **Red background** = Core module",
            "- Default background = Related module",
            f"- **Total Files**: {len(file_nodes)}",
            f"- **Import Relationships**: {len(seen_imports)}",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _export_mermaid_all(
    nodes: list[NodeInfo],
    edges: list[EdgeInfo],
    repo_root: Path,
    output_dir: Path,
    max_nodes: int = 500,
) -> list[str]:
    """Export multiple Mermaid diagram files with full information."""
    output_files = []

    file_nodes = [n for n in nodes if n.kind == "File"]
    class_nodes = [n for n in nodes if n.kind == "Class"]
    func_nodes = [n for n in nodes if n.kind in ("Function", "Test")]

    edges_by_kind: dict[str, list[EdgeInfo]] = defaultdict(list)
    for edge in edges:
        edges_by_kind[edge.kind].append(edge)

    summary_path = output_dir / "00-summary.md"
    _export_summary_diagram(
        file_nodes, edges_by_kind.get("IMPORTS_FROM", []), repo_root, summary_path
    )
    output_files.append(str(summary_path))

    calls_path = output_dir / "01-calls-all.md"
    _export_calls_diagram(
        class_nodes,
        func_nodes,
        edges_by_kind.get("CALLS", []),
        repo_root,
        calls_path,
        max_nodes,
    )
    output_files.append(str(calls_path))

    inherits_edges = edges_by_kind.get("INHERITS", []) + edges_by_kind.get(
        "IMPLEMENTS", []
    )
    if inherits_edges:
        inherits_path = output_dir / "02-inherits.md"
        _export_inherits_diagram(class_nodes, inherits_edges, repo_root, inherits_path)
        output_files.append(str(inherits_path))

    test_edges = edges_by_kind.get("TESTED_BY", [])
    if test_edges:
        tests_path = output_dir / "03-tests.md"
        _export_tests_diagram(func_nodes, test_edges, repo_root, tests_path)
        output_files.append(str(tests_path))

    by_module_dir = output_dir / "by-module"
    by_module_dir.mkdir(parents=True, exist_ok=True)
    module_files = _export_by_module(
        class_nodes, func_nodes, edges_by_kind, repo_root, by_module_dir, max_nodes
    )
    output_files.extend(module_files)

    return output_files


def _export_summary_diagram(
    file_nodes: list[NodeInfo],
    import_edges: list[EdgeInfo],
    repo_root: Path,
    output_path: Path,
) -> None:
    """Export file-level summary diagram."""
    lines = [
        "# Code Graph - Summary (File Level)",
        "",
        f"Generated from: `{repo_root}`",
        "",
        "```mermaid",
        "graph TD",
    ]

    file_ids: dict[str, str] = {}
    for i, node in enumerate(file_nodes):
        rel_path = _relative_path(node.file_path, repo_root)
        node_id = f"f{i}"
        file_ids[node.file_path] = node_id
        lines.append(f'    {node_id}["{rel_path}"]')

    seen_imports = set()
    for edge in import_edges:
        source_file = edge.file_path
        target = edge.target
        target_file = None
        for fp in file_ids:
            if (
                target in fp
                or fp.endswith(target)
                or target.endswith(_relative_path(fp, repo_root))
            ):
                target_file = fp
                break

        if source_file in file_ids and target_file and target_file in file_ids:
            key = (source_file, target_file)
            if key not in seen_imports:
                seen_imports.add(key)
                lines.append(
                    f"    {file_ids[source_file]} -->|imports| {file_ids[target_file]}"
                )

    lines.extend(
        [
            "```",
            "",
            f"**Total Files**: {len(file_nodes)}",
            f"**Import Relationships**: {len(seen_imports)}",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _export_calls_diagram(
    class_nodes: list[NodeInfo],
    func_nodes: list[NodeInfo],
    call_edges: list[EdgeInfo],
    repo_root: Path,
    output_path: Path,
    max_nodes: int,
) -> None:
    """Export all CALLS relationships as Mermaid diagrams."""
    lines = [
        "# Code Graph - All Function Calls",
        "",
        f"Generated from: `{repo_root}`",
        "",
        f"Total call relationships: {len(call_edges)}",
        "",
    ]

    nodes_by_file: dict[str, list[NodeInfo]] = defaultdict(list)
    for n in class_nodes + func_nodes:
        nodes_by_file[n.file_path].append(n)

    if len(nodes_by_file) > 15 or len(call_edges) > 500:
        lines.append("## Diagrams by Module")
        lines.append("")

        modules = defaultdict(lambda: defaultdict(list))
        for file_path, file_nodes_list in nodes_by_file.items():
            rel_path = _relative_path(file_path, repo_root)
            module = rel_path.split("/")[0] if "/" in rel_path else "root"
            modules[module][file_path] = file_nodes_list

        for module_name, module_files in sorted(modules.items()):
            module_nodes = []
            for file_nodes_list in module_files.values():
                module_nodes.extend(file_nodes_list)

            module_qnames = {_qualify(n) for n in module_nodes}
            module_edges = [
                e
                for e in call_edges
                if e.source in module_qnames or e.target in module_qnames
            ]

            if module_nodes:
                lines.append(f"### Module: {module_name}")
                lines.append("")
                lines.append("```mermaid")
                lines.append("graph TD")

                node_ids: dict[str, str] = {}
                counter = [0]

                def get_id(
                    qname: str, _node_ids: dict = node_ids, _counter: list = counter
                ) -> str:
                    if qname not in _node_ids:
                        _node_ids[qname] = f"n{_counter[0]}"
                        _counter[0] += 1
                    return _node_ids[qname]

                for n in module_nodes[:max_nodes]:
                    qname = _qualify(n)
                    node_id = get_id(qname)
                    if n.kind == "Class":
                        lines.append(f'    {node_id}[["{n.name}"]]')
                    elif n.kind == "Test":
                        lines.append(f'    {node_id}("{n.name}")')
                    else:
                        lines.append(f'    {node_id}["{n.name}"]')

                seen = set()
                for edge in module_edges[:500]:
                    source_id = get_id(edge.source)
                    target_id = get_id(edge.target)
                    key = (edge.source, edge.target)
                    if key not in seen:
                        seen.add(key)
                        lines.append(f"    {source_id} -->|calls| {target_id}")

                lines.append("```")
                lines.append("")
    else:
        lines.append("```mermaid")
        lines.append("graph TD")

        node_ids: dict[str, str] = {}
        counter = [0]

        def get_id(qname: str) -> str:
            if qname not in node_ids:
                node_ids[qname] = f"n{counter[0]}"
                counter[0] += 1
            return node_ids[qname]

        for file_path, file_nodes_list in sorted(nodes_by_file.items()):
            rel_path = _relative_path(file_path, repo_root)
            subgraph_id = rel_path.replace("/", "_").replace(".", "_").replace("-", "_")
            lines.append(f'    subgraph {subgraph_id}["{rel_path}"]')

            for n in file_nodes_list:
                qname = _qualify(n)
                node_id = get_id(qname)
                if n.kind == "Class":
                    lines.append(f'        {node_id}[["{n.name}"]]')
                elif n.kind == "Test":
                    lines.append(f'        {node_id}("{n.name}")')
                else:
                    lines.append(f'        {node_id}["{n.name}"]')

            lines.append("    end")

        seen = set()
        for edge in call_edges:
            source_id = get_id(edge.source)
            target_id = get_id(edge.target)
            key = (edge.source, edge.target)
            if key not in seen:
                seen.add(key)
                lines.append(f"    {source_id} -->|calls| {target_id}")

        lines.append("```")
        lines.extend(
            [
                "",
                "## Legend",
                "",
                "- `[[Class]]` - Class nodes",
                "- `[Function]` - Function nodes",
                "- `(Test)` - Test nodes",
                "- `-->` - Calls relationship",
            ]
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _export_inherits_diagram(
    class_nodes: list[NodeInfo],
    inherits_edges: list[EdgeInfo],
    repo_root: Path,
    output_path: Path,
) -> None:
    """Export inheritance hierarchy as Mermaid diagram."""
    lines = [
        "# Code Graph - Inheritance Hierarchy",
        "",
        f"Generated from: `{repo_root}`",
        "",
        f"Total inheritance relationships: {len(inherits_edges)}",
        "",
        "```mermaid",
        "graph TD",
    ]

    node_ids: dict[str, str] = {}
    counter = [0]

    def get_id(name: str) -> str:
        if name not in node_ids:
            node_ids[name] = f"c{counter[0]}"
            counter[0] += 1
        return node_ids[name]

    for n in class_nodes:
        qname = _qualify(n)
        node_id = get_id(qname)
        lines.append(f'    {node_id}[["{n.name}"]]')

    for edge in inherits_edges:
        source_id = get_id(edge.source)
        target_id = get_id(edge.target)
        label = "extends" if edge.kind == "INHERITS" else "implements"
        lines.append(f"    {source_id} -->|{label}| {target_id}")

    lines.extend(
        [
            "```",
            "",
            "## Legend",
            "",
            "- `[[Class]]` - Class nodes",
            "- `-->|extends|` - Inheritance",
            "- `-->|implements|` - Interface implementation",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _export_tests_diagram(
    func_nodes: list[NodeInfo],
    test_edges: list[EdgeInfo],
    repo_root: Path,
    output_path: Path,
) -> None:
    """Export test relationships as Mermaid diagram."""
    lines = [
        "# Code Graph - Test Coverage",
        "",
        f"Generated from: `{repo_root}`",
        "",
        f"Total test relationships: {len(test_edges)}",
        "",
        "```mermaid",
        "graph LR",
    ]

    node_ids: dict[str, str] = {}
    counter = [0]

    def get_id(name: str) -> str:
        if name not in node_ids:
            node_ids[name] = f"t{counter[0]}"
            counter[0] += 1
        return node_ids[name]

    test_funcs = {e.target for e in test_edges}
    prod_funcs = {e.source for e in test_edges}

    for func_name in prod_funcs:
        node_id = get_id(func_name)
        short_name = func_name.split("::")[-1]
        lines.append(f'    {node_id}["{short_name}"]')

    for func_name in test_funcs:
        node_id = get_id(func_name)
        short_name = func_name.split("::")[-1]
        lines.append(f'    {node_id}("{short_name}")')

    for edge in test_edges:
        source_id = get_id(edge.source)
        target_id = get_id(edge.target)
        lines.append(f"    {source_id} -->|tested by| {target_id}")

    lines.extend(
        [
            "```",
            "",
            "## Legend",
            "",
            "- `[Function]` - Production code",
            "- `(Test)` - Test function",
            "- `-->|tested by|` - Test relationship",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _export_by_module(
    class_nodes: list[NodeInfo],
    func_nodes: list[NodeInfo],
    edges_by_kind: dict[str, list[EdgeInfo]],
    repo_root: Path,
    output_dir: Path,
    max_nodes: int,
) -> list[str]:
    """Export detailed diagrams by module/directory."""
    output_files = []

    modules: dict[str, dict] = defaultdict(lambda: {"classes": [], "functions": []})

    for n in class_nodes:
        rel_path = _relative_path(n.file_path, repo_root)
        module = rel_path.split("/")[0] if "/" in rel_path else "root"
        modules[module]["classes"].append(n)

    for n in func_nodes:
        rel_path = _relative_path(n.file_path, repo_root)
        module = rel_path.split("/")[0] if "/" in rel_path else "root"
        modules[module]["functions"].append(n)

    all_call_edges = edges_by_kind.get("CALLS", [])
    all_inherits_edges = edges_by_kind.get("INHERITS", []) + edges_by_kind.get(
        "IMPLEMENTS", []
    )

    for module_name, module_data in sorted(modules.items()):
        if not module_data["classes"] and not module_data["functions"]:
            continue

        output_path = output_dir / f"{module_name.replace('/', '_')}.md"

        lines = [
            f"# Module: {module_name}",
            "",
            f"Generated from: `{repo_root}`",
            "",
        ]

        module_qnames = set()
        for n in module_data["classes"] + module_data["functions"]:
            module_qnames.add(_qualify(n))

        module_calls = [
            e
            for e in all_call_edges
            if e.source in module_qnames or e.target in module_qnames
        ]
        module_inherits = [
            e
            for e in all_inherits_edges
            if e.source in module_qnames or e.target in module_qnames
        ]

        lines.append(f"- Classes: {len(module_data['classes'])}")
        lines.append(f"- Functions: {len(module_data['functions'])}")
        lines.append(f"- Call relationships: {len(module_calls)}")
        lines.append(f"- Inheritance relationships: {len(module_inherits)}")
        lines.append("")

        lines.append("```mermaid")
        lines.append("graph TD")

        node_ids: dict[str, str] = {}
        counter = [0]

        def get_id(
            qname: str, _node_ids: dict = node_ids, _counter: list = counter
        ) -> str:
            if qname not in _node_ids:
                _node_ids[qname] = f"n{_counter[0]}"
                _counter[0] += 1
            return _node_ids[qname]

        for n in module_data["classes"][:max_nodes]:
            qname = _qualify(n)
            node_id = get_id(qname)
            lines.append(f'    {node_id}[["{n.name}"]]')

        for n in module_data["functions"][:max_nodes]:
            qname = _qualify(n)
            node_id = get_id(qname)
            if n.kind == "Test":
                lines.append(f'    {node_id}("{n.name}")')
            else:
                lines.append(f'    {node_id}["{n.name}"]')

        seen = set()
        for edge in module_calls[:300]:
            source_id = get_id(edge.source)
            target_id = get_id(edge.target)
            key = (edge.source, edge.target)
            if key not in seen:
                seen.add(key)
                lines.append(f"    {source_id} -->|calls| {target_id}")

        for edge in module_inherits[:100]:
            source_id = get_id(edge.source)
            target_id = get_id(edge.target)
            label = "extends" if edge.kind == "INHERITS" else "implements"
            lines.append(f"    {source_id} -->|{label}| {target_id}")

        lines.append("```")

        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        output_files.append(str(output_path))

    return output_files


# ── Summary JSON export (lightweight, for module discovery) ──────────────────


def _export_summary_json(
    node_dicts: list[dict],
    edge_dicts: list[dict],
    code_size: CodeSize,
    repo_root: Path,
    output_path: Path,
) -> None:
    """Export a lightweight summary JSON for module discovery.

    This file contains only:
    - File paths (from File nodes)
    - Node/edge kind counts
    - Code size statistics

    It allows ModuleDiscovery to load a few KB instead of a 400+ MB graph-raw.json.
    """
    # Extract file paths from File nodes
    file_paths = sorted(
        {n.get("file_path", "") for n in node_dicts if n.get("kind") == "File"}
    )

    # Count nodes by kind
    node_kinds: dict[str, int] = {}
    for n in node_dicts:
        kind = n.get("kind", "Unknown")
        node_kinds[kind] = node_kinds.get(kind, 0) + 1

    # Count edges by kind
    edge_kinds: dict[str, int] = {}
    for e in edge_dicts:
        kind = e.get("kind", "Unknown")
        edge_kinds[kind] = edge_kinds.get(kind, 0) + 1

    summary = {
        "metadata": {
            "generated_from": str(repo_root),
            "total_nodes": len(node_dicts),
            "total_edges": len(edge_dicts),
            "file_count": len(file_paths),
        },
        "files": file_paths,
        "node_kinds": node_kinds,
        "edge_kinds": edge_kinds,
        "code_size": {
            "total_files": code_size.total_files,
            "total_lines": code_size.total_lines,
            "total_bytes": code_size.total_bytes,
            "by_extension": code_size.by_extension,
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


# ── Utility functions ─────────────────────────────────────────────────────────


def _qualify(node: NodeInfo) -> str:
    """Create qualified name for a node."""
    if node.parent_name:
        return f"{node.file_path}::{node.parent_name}.{node.name}"
    return f"{node.file_path}::{node.name}"


def _qualify_dict(n: dict) -> str:
    """Create qualified name for a dict node."""
    file_path = n.get("file_path", "")
    parent = n.get("parent_name")
    name = n.get("name", "")
    if parent:
        return f"{file_path}::{parent}.{name}"
    return f"{file_path}::{name}"


def _relative_path(path: str, repo_root: Path) -> str:
    """Convert absolute path to relative path."""
    try:
        return str(Path(path).relative_to(repo_root))
    except ValueError:
        return path


def _shorten_name(name: str, repo_root: Path) -> str:
    """Shorten a qualified name for display."""
    for prefix in [str(repo_root) + "/", str(repo_root) + "::"]:
        if name.startswith(prefix):
            name = name[len(prefix) :]
            break
    return name
