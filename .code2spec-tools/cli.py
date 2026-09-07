#!/usr/bin/env python3
"""CLI entry point for code-to-ast."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    from .analysis_paths import (
        check_required_delta_state,
        get_canonical_paths,
        migrate_analysis_dir,
        needs_migration,
    )
except ImportError:
    from analysis_paths import (
        check_required_delta_state,
        get_canonical_paths,
        migrate_analysis_dir,
        needs_migration,
    )

_PYPI_INDEX = "https://bart.sec.samsung.net/artifactory/api/pypi/pypi-remote/simple"
_REQUIRED = [
    ("tree_sitter", "tree-sitter>=0.26,<0.27"),
    ("tree_sitter_language_pack", "tree-sitter-language-pack>=1.0.0,<2"),
    ("networkx", "networkx>=3.2,<4"),
]


def ensure_deps() -> None:
    """Check required packages are installed. Exits with error if any are missing."""
    missing = [spec for pkg, spec in _REQUIRED if not _importable(pkg)]
    if not missing:
        return

    print(
        "[code-to-ast] ERROR: required packages are not installed.\n"
        "  Run install.py (or install.sh) first to set up dependencies.\n"
        f"  Missing: {', '.join(missing)}\n"
        f"\n"
        f"  Or install manually:\n"
        f"    python3 -m pip install --index-url {_PYPI_INDEX} {' '.join(missing)}",
        file=sys.stderr,
    )
    sys.exit(1)


def _importable(name: str) -> bool:
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def main() -> None:
    ensure_deps()
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="code-to-ast",
        description="Extract AST from code using tree-sitter and export as structured data",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # export command
    export_parser = subparsers.add_parser(
        "export", help="Export AST graph as Markdown files"
    )
    export_parser.add_argument(
        "--format",
        choices=["raw", "mermaid", "both"],
        default="both",
        help="Export format (default: both)",
    )
    export_parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Repository or subdirectory root to analyze (auto-detected)",
    )
    export_parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="AST output directory (default: <repo>/.code-to-ast or caller-provided path)",
    )
    export_parser.add_argument(
        "--workers",
        type=int,
        default=-1,
        help="병렬 파싱 워커 수 (기본값: -1=자동, 최대 16)",
    )
    export_parser.add_argument(
        "--benchmark",
        action="store_true",
        help="phase별 성능 계측 결과 출력",
    )
    export_parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="파싱 캐시 디렉토리 (기본값: .code-to-ast/.cache/)",
    )
    export_parser.add_argument(
        "--no-cache",
        action="store_true",
        help="파싱 캐시 비활성화",
    )

    # discover-ipc command (IPC Pattern Discovery via LLM)
    discover_ipc_parser = subparsers.add_parser(
        "discover-ipc",
        help="Discover IPC patterns via LLM for dynamic IPC mechanism detection",
    )
    discover_ipc_parser.add_argument(
        "--source-dir",
        type=Path,
        required=True,
        help="Source directory to scan for unmatched IPC call patterns",
    )
    discover_ipc_parser.add_argument(
        "--language",
        required=True,
        help="Programming language to discover IPC patterns for (e.g. java, python, kotlin)",
    )
    discover_ipc_parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for IPC discovery prompt and patterns (default: <source-dir>/.ipc-discovery/)",
    )
    discover_ipc_parser.add_argument(
        "--max-files",
        type=int,
        default=20,
        help="Maximum number of source files to scan (default: 20)",
    )
    discover_ipc_parser.add_argument(
        "--step",
        choices=["prompt", "apply"],
        default="prompt",
        help="'prompt' = generate LLM prompt only; 'apply' = process LLM response and apply patterns",
    )
    discover_ipc_parser.add_argument(
        "--llm-response",
        type=Path,
        default=None,
        help="LLM response file to process (required when --step=apply)",
    )

    # llm-extract command (delegates to llm_extract_cli.py)
    llm_extract_parser = subparsers.add_parser(
        "llm-extract",
        help="LLM-based ENUM/Constant/IPC extraction from AST JSON",
    )
    llm_extract_parser.add_argument(
        "--ast-json",
        type=str,
        default=None,
        help="Path to AST JSON file (graph-raw.json) for extraction",
    )
    llm_extract_parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="llm-extraction-results.json",
        help="Path to save extraction results",
    )
    llm_extract_parser.add_argument(
        "--extract",
        type=str,
        action="append",
        choices=["enum", "constant", "ipc", "all"],
        default=None,
        help="What to extract (can specify multiple)",
    )
    llm_extract_parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save prompt and result files",
    )
    llm_extract_parser.add_argument(
        "--load-results",
        type=str,
        default=None,
        help="Load previously saved results from directory",
    )
    llm_extract_parser.add_argument(
        "--validate",
        action="store_true",
        default=False,
        help="Validate extraction completeness against AST JSON",
    )
    llm_extract_parser.add_argument(
        "--parse-response",
        type=str,
        default=None,
        help="Parse a saved LLM response file",
    )
    llm_extract_parser.add_argument(
        "--parse-type",
        type=str,
        choices=["enum", "constant", "ipc"],
        default=None,
        help="Type of extraction when using --parse-response",
    )
    llm_extract_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    llm_extract_parser.add_argument(
        "--hybrid-auto",
        action="store_true",
        help="Use hybrid approach: rule-based pre-extraction + LLM gap-fill",
    )
    llm_extract_parser.add_argument(
        "--min-enum",
        type=int,
        default=None,
        help="Fail --validate if fewer than N ENUMs were extracted",
    )
    llm_extract_parser.add_argument(
        "--min-constant",
        type=int,
        default=None,
        help="Fail --validate if fewer than N constants were extracted",
    )
    llm_extract_parser.add_argument(
        "--min-ipc",
        type=int,
        default=None,
        help="Fail --validate if fewer than N IPC patterns were extracted",
    )
    llm_extract_parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from partial extraction if interrupted",
    )
    llm_extract_parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Maximum retry attempts per LLM chunk on failure",
    )

    # delta-plan command
    delta_parser = subparsers.add_parser(
        "delta-plan",
        help="기존 spec-cache와 비교해 변경 분류(diff-plan.json) 생성",
    )
    delta_parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Repository or subdirectory root to diff (auto-detected)",
    )
    delta_parser.add_argument(
        "--analysis-dir",
        type=Path,
        required=True,
        help="code2spec/.analysis 디렉토리 경로 " "(canonical state/delta 위치 기준)",
    )
    delta_parser.add_argument(
        "--save-to",
        type=Path,
        default=None,
        help="diff-plan.json 저장 경로 (기본: <analysis-dir>/state/delta/diff-plan.json)",
    )
    delta_parser.add_argument(
        "--code2spec-version",
        default=None,
        help="현재 code2spec 버전 (무효화 판정용)",
    )
    delta_parser.add_argument(
        "--module-groups",
        default="",
        help="module-groups.yaml 경로 (Logical Module 시 파일 단위 diff를 모듈 단위로 집계)",
    )
    delta_parser.add_argument(
        "--quiet",
        action="store_true",
        help="요약만 출력 (모듈별 라인 생략)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "export":
        try:
            from .exporter import export_graph
        except ImportError:  # script/installed-tools flat execution
            from exporter import export_graph

        repo_root = args.repo or Path.cwd()

        # Resolve workers: -1 = auto (min(cpu_count, 16))
        workers = args.workers
        if workers <= 0:
            workers = min(os.cpu_count() or 4, 16)

        result = export_graph(
            repo_root=repo_root,
            output_dir=args.output_dir,
            format=args.format,
            workers=workers,
            cache_dir=args.cache_dir,
            no_cache=args.no_cache,
            benchmark=args.benchmark,
        )
        print(
            f"Exported {result['files_parsed']} files, {result['total_nodes']} nodes, {result['total_edges']} edges"
        )
        for f in result["output_files"]:
            print(f"  - {f}")

    elif args.command == "discover-ipc":
        _run_discover_ipc(args)

    elif args.command == "llm-extract":
        _run_llm_extract(args)

    elif args.command == "delta-plan":
        _run_delta_plan(args)


def _run_discover_ipc(args) -> None:
    """discover-ipc: LLM-based IPC pattern discovery for dynamic IPC mechanism detection."""
    try:
        from .ipc_discovery import (
            apply_ipc_patterns,
            build_ipc_discovery_prompt,
            collect_unmatched_calls,
            parse_ipc_discovery_response,
        )
    except ImportError:
        from ipc_discovery import (
            apply_ipc_patterns,
            build_ipc_discovery_prompt,
            collect_unmatched_calls,
            parse_ipc_discovery_response,
        )

    source_dir = str(args.source_dir)
    language = args.language
    output_dir = (
        str(args.output_dir)
        if args.output_dir
        else os.path.join(source_dir, ".ipc-discovery")
    )
    os.makedirs(output_dir, exist_ok=True)

    if args.step == "prompt":
        # Step 1: Collect unmatched calls
        unmatched_calls, files_scanned = collect_unmatched_calls(
            source_dir,
            language,
            max_files=args.max_files,
        )
        print(
            f"[ipc-discovery] Collected {len(unmatched_calls)} unmatched calls from {files_scanned} files"
        )
        if files_scanned == 0:
            # Scanning nothing is indistinguishable from "this project has no
            # IPC" in the downstream catalog — say so instead of proceeding
            # quietly with an empty prompt.
            print(
                f"[ipc-discovery] WARNING: no {language} file under {source_dir} could be "
                "scanned. The prompt below is empty and the IPC catalog will be blank. "
                "Check --language/--source-dir and the warnings above.",
                file=sys.stderr,
            )

        # Step 2: Generate LLM prompt
        prompt = build_ipc_discovery_prompt(language, unmatched_calls, files_scanned)
        prompt_path = os.path.join(output_dir, "llm-prompt.md")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"[ipc-discovery] Prompt saved to: {prompt_path}")
        print(
            "\n[ipc-discovery] Next steps:\n"
            "  1. Read the generated prompt file and send it to Cline LLM\n"
            "  2. Save the LLM response to a file\n"
            "  3. Run: code-to-ast discover-ipc --step apply "
            f"--source-dir {source_dir} --language {language} "
            f"--llm-response <response-file>"
        )

    elif args.step == "apply":
        # Step 3: Process LLM response and apply patterns
        if not args.llm_response:
            print(
                "[ipc-discovery] ERROR: --llm-response is required when --step=apply",
                file=sys.stderr,
            )
            sys.exit(1)

        llm_response_path = args.llm_response
        if not llm_response_path.exists():
            print(
                f"[ipc-discovery] ERROR: LLM response file not found: {llm_response_path}",
                file=sys.stderr,
            )
            sys.exit(1)

        llm_response = llm_response_path.read_text(encoding="utf-8")
        patterns = parse_ipc_discovery_response(llm_response, language)
        apply_ipc_patterns(patterns, language)

        # Save applied patterns to JSON
        patterns_path = os.path.join(output_dir, "discovered-ipc-patterns.json")
        import json

        with open(patterns_path, "w", encoding="utf-8") as f:
            json.dump({"language": language, "patterns": patterns}, f, indent=2)

        print(
            f"\n[ipc-discovery] Applied {len(patterns)} IPC patterns for {language}\n"
            f"  Patterns saved to: {patterns_path}\n"
            f"  Note: Patterns are applied at runtime. For persistence, re-run export with these patterns."
        )


def _run_delta_plan(args) -> None:
    """delta-plan: 현재 소스 파일 vs spec-cache 비교 → diff-plan.json.

    W-DELTA startup 시 마이그레이션을 먼저 실행한 후 필수 delta state 를 검증한다.
    """
    try:
        from .delta.spec_cache import (
            compute_diff_plan,
            load_core_manifest,
            load_source_deps_map,
            load_spec_cache,
            save_diff_plan,
        )
        from .exporter import _collect_source_files
    except ImportError:  # script/installed-tools flat execution
        from delta.spec_cache import (
            compute_diff_plan,
            load_core_manifest,
            load_source_deps_map,
            load_spec_cache,
            save_diff_plan,
        )
        from exporter import _collect_source_files

    repo_root: Path = args.repo or Path.cwd()
    analysis_dir: Path = args.analysis_dir

    # Step 1: Run migration if needed (before prerequisite validation)
    if needs_migration(analysis_dir):
        print("[delta-plan] Running .analysis migration...")
        report = migrate_analysis_dir(analysis_dir)
        print(f"  Migration status: {report.status}")
        if report.moved:
            print(f"  Moved {len(report.moved)} artifacts to canonical locations")
        if report.quarantined:
            print(f"  Quarantined {len(report.quarantined)} unknown artifacts")
        if report.conflicts:
            print(f"  {len(report.conflicts)} conflicts preserved in quarantine")
        if report.warnings:
            for warning in report.warnings:
                print(f"  ⚠ {warning}")

    # Step 2: Check required delta state
    paths = get_canonical_paths(analysis_dir)
    is_valid, error_msg = check_required_delta_state(analysis_dir)
    if not is_valid:
        print(f"[ERROR] {error_msg}")
        print(
            "  → Run full rebuild: /code2spec-discovery -> /code2spec-modules -> /code2spec-finalize"
        )
        sys.exit(1)

    # Use canonical paths
    spec_cache_path = paths.spec_cache
    diff_plan_path = args.save_to or paths.diff_plan

    spec_cache = load_spec_cache(spec_cache_path)

    # core-manifest.json 로드 (Core 승격/강등 감지)
    core_manifest = load_core_manifest(paths.core_manifest)

    # source-deps-map.json 로드 (간접 의존성 추적)
    source_deps_map = load_source_deps_map(paths.source_deps_map)

    source_files = _collect_source_files(repo_root)

    # Logical Module: module_groups_path를 compute_diff_plan에 전달
    module_groups_path = getattr(args, "module_groups", "") or ""

    plan = compute_diff_plan(
        source_files,
        spec_cache,
        core_manifest=core_manifest,
        source_deps_map=source_deps_map,
        module_groups_path=module_groups_path,
        repo_root=repo_root,
    )

    # Logical Module: 파일 단위 diff를 모듈 단위로 집계
    if module_groups_path:
        try:
            from .delta.spec_cache import aggregate_diff_plan_by_modules
        except ImportError:
            from delta.spec_cache import aggregate_diff_plan_by_modules
        plan = aggregate_diff_plan_by_modules(
            plan, module_groups_path, repo_root=repo_root
        )

    # spec-cache 없을 때 자동 full build 유도
    if spec_cache is None:
        print("  ⚠ spec-cache.json not found. Full build is required.")
        print("  → Run /code2spec-discovery for full build.")

    save_diff_plan(diff_plan_path, plan)

    summary = plan.to_dict()["summary"]
    print(
        f"[delta-plan] Unchanged: {summary['unchanged']}, "
        f"Changed: {summary['changed']}, "
        f"New: {summary['new']}, "
        f"Promoted: {summary['promoted']}, "
        f"Dependent Changed: {summary['dependent_changed']}, "
        f"Removed: {summary['removed']}, "
        f"Peripheral New: {summary['peripheral_new']}, "
        f"Peripheral Changed: {summary['peripheral_changed']}, "
        f"Moved: {summary['moved']}"
    )
    if plan.invalidated:
        print(f"  ⚠ cache invalidated: {plan.invalidated_reason}")
        print("  → full rebuild recommended (W1+W2+W3).")
    elif not plan.needs_work:
        print("  No source changes detected. Only quick-reference will refresh.")
    else:
        # 임계값 경고
        if plan.regen_ratio > 0.5:
            print(
                f"  ⚠ Regeneration target exceeds 50% of core modules "
                f"({plan.regen_ratio:.0%}). Full rebuild recommended."
            )
        if not args.quiet:
            for kind, items in (
                ("changed", plan.changed),
                ("promoted", plan.promoted),
                ("dependent_changed", plan.dependent_changed),
                ("new", plan.new),
                ("removed", plan.removed),
                ("peripheral_new", plan.peripheral_new),
                ("peripheral_changed", plan.peripheral_changed),
                ("moved", plan.moved),
            ):
                if not items:
                    continue
                print(f"  {kind}:")
                for item in items[:20]:
                    if kind == "moved":
                        print(f"    - {item['from']} → {item['to']}")
                    elif kind == "dependent_changed":
                        rel = _relative_to(item["file"], repo_root)
                        dep = _relative_to(item["changed_dep"], repo_root)
                        print(f"    - {rel} ← {dep} (indirect)")
                    else:
                        rel = _relative_to(item["file"], repo_root)
                        print(f"    - {rel}")
                if len(items) > 20:
                    print(f"    ... +{len(items) - 20} more")
    print(f"  → {diff_plan_path}")


def _run_llm_extract(args) -> None:
    """llm-extract: delegates to llm_extract_cli.main() with parsed args."""
    try:
        from . import llm_extract_cli
    except ImportError:
        import llm_extract_cli

    # Reconstruct sys.argv so llm_extract_cli.parse_args() picks up the flags
    import sys as _sys

    _sys.argv = ["code-to-ast llm-extract"] + _sys.argv[2:]
    llm_extract_cli.main()


def _relative_to(file_path: str, repo_root: Path) -> str:
    try:
        return str(Path(file_path).relative_to(repo_root))
    except ValueError:
        return file_path


if __name__ == "__main__":
    main()
