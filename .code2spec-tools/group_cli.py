#!/usr/bin/env python3
"""Module Grouping CLI - HITL (Human-in-the-Loop) 모듈 그룹핑 도구."""

from __future__ import annotations

import argparse
import json
import os
import sys

try:
    from .config_loader import load_config, validate_config
    from .module_coverage import CoverageReport, validate_module_coverage
    from .module_discovery import DiscoveredModule, ModuleDiscovery
except ImportError:  # script/installed-tools flat execution
    from config_loader import load_config, validate_config
    from module_coverage import CoverageReport, validate_module_coverage
    from module_discovery import DiscoveredModule, ModuleDiscovery


def cmd_discover(args: argparse.Namespace) -> int:
    """LLM Module Discovery 실행."""
    print("[group-cli] Running Module Discovery...")
    print(f"  AST dir: {args.ast_dir}")
    print(f"  Output dir: {args.output_dir}")
    print(f"  Strategy: {args.strategy}")
    print(f"  Prompt file limit: {args.prompt_file_limit}")
    print(f"  Large repo mode: {args.large_repo_mode}")
    if args.large_repo_mode in {'auto', 'hierarchy'}:
        print(f"  Hierarchy maximum modules: {args.hierarchy_max_modules}")

    discovery = ModuleDiscovery(args.ast_dir, args.output_dir)
    discovery.load_graph()

    # 그래프 정보 출력
    summary = discovery.get_graph_summary()
    print(f"  Files: {summary['file_count']}")
    print(f"  Nodes: {summary['total_nodes']}, Edges: {summary['total_edges']}")

    # 프롬프트 생성
    prompt = discovery.build_prompt(
        template=args.prompt,
        prompt_file_limit=args.prompt_file_limit,
        large_repo_mode=args.large_repo_mode,
        hierarchy_max_modules=args.hierarchy_max_modules,
    )
    prompt_path = os.path.join(args.output_dir, 'llm-prompt.md')
    os.makedirs(args.output_dir, exist_ok=True)
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    print(f"  Prompt saved to: {prompt_path}")

    print("\n[group-cli] Next step:")
    print("  1. Send the prompt to LLM")
    print("  2. Save LLM response to a file")
    print("  3. Run: group-cli review --llm-response <response-file>")

    return 0


def cmd_review(args: argparse.Namespace) -> int:
    """LLM 응답 검토 및 HITL 병합."""
    print("[group-cli] Reviewing LLM response...")

    # AST 그래프 로드
    discovery = ModuleDiscovery(args.ast_dir, args.output_dir)
    discovery.load_graph()

    # LLM 응답 읽기
    with open(args.llm_response, encoding='utf-8') as f:
        llm_response = f.read()

    # 파싱
    modules = discovery.discover(
        llm_response,
        allow_broad_patterns=args.allow_broad_patterns,
    )
    print(f"  Discovered {len(modules)} modules:")

    for i, mod in enumerate(modules, 1):
        print(f"\n  {i}. {mod['name'] if isinstance(mod, dict) else mod.name} ({len(mod['files']) if isinstance(mod, dict) else len(mod.files)} files)")
        print(f"     Confidence: {mod.get('confidence', 0) if isinstance(mod, dict) else mod.confidence}")
        print(f"     Rationale: {(mod.get('rationale', '') if isinstance(mod, dict) else mod.rationale)[:60]}...")

    report = validate_module_coverage(modules, set(discovery._files))
    if not report.ok:
        _print_coverage_failure(report)
        _write_coverage_artifacts(args.output_dir, report, modules)
        return 1

    # YAML 로 저장
    output_path = os.path.join(args.output_dir, args.output or 'module-groups-proposed.yaml')
    discovery.save_results(modules, output_path)

    print(f"\n[group-cli] Proposed modules saved to: {output_path}")
    print("  Edit the file if needed, then run:")
    print(f"  group-cli save --config {output_path}")

    return 0


def _print_coverage_failure(report: CoverageReport) -> None:
    """Print concise coverage validation failure summary."""
    print("\n[group-cli] ❌ Module coverage validation failed:")
    print(f"  Known files: {report.known_count}")
    print(f"  Assigned files: {report.assigned_count} ({report.assigned_unique_count} unique)")

    checks = [
        ("Missing files", report.missing_files),
        ("Unknown files", report.unknown_files),
        ("Duplicate files", report.duplicate_files),
        ("Empty modules", report.empty_modules),
        ("Unmatched patterns", report.unmatched_patterns),
        ("Broad patterns", report.broad_patterns),
    ]
    for label, values in checks:
        if values:
            preview = ", ".join(values[:8])
            suffix = f" ... +{len(values) - 8} more" if len(values) > 8 else ""
            print(f"  - {label}: {len(values)} ({preview}{suffix})")


def _write_coverage_artifacts(
    output_dir: str,
    report: CoverageReport,
    modules: list[DiscoveredModule],
) -> None:
    """Write deterministic artifacts that help humans repair LLM output."""
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, 'coverage-report.json')
    repair_path = os.path.join(output_dir, 'repair-prompt.md')

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)

    module_summary = "\n".join(
        f"- {module.name}: {len(module.files)} files"
        for module in modules
    )
    repair_prompt = f"""# Logical Module Coverage Repair

The previous LLM module proposal failed deterministic Python validation.
Revise the YAML so every known file is assigned exactly once.

## Current module summary
{module_summary}

## Validation report
```json
{json.dumps(report.to_dict(), ensure_ascii=False, indent=2)}
```

## Repair rules
- Add every missing file to exactly one semantically appropriate module.
- Remove unknown files that are not in the known manifest.
- Resolve duplicate files by keeping each file in only one module.
- Replace unmatched include/exclude patterns with valid paths or patterns.
- Replace broad include patterns with narrower directory or feature patterns.
- Do not create placeholder modules such as `other` unless the project genuinely requires it.
"""
    with open(repair_path, 'w', encoding='utf-8') as f:
        f.write(repair_prompt)

    print(f"  Coverage report saved to: {report_path}")
    print(f"  Repair prompt saved to: {repair_path}")


def cmd_save(args: argparse.Namespace) -> int:
    """최종 모듈 설정 저장."""
    print("[group-cli] Saving module groups...")

    # 설정 로드 및 검증
    config = load_config(args.config)
    errors = validate_config(config)

    if errors:
        print("[group-cli] ⚠️  Validation errors:")
        for err in errors:
            print(f"    - {err}")
        if not args.force:
            print("[group-cli] Use --force to save anyway")
            return 1

    # 저장
    output_path = os.path.join(args.output_dir, 'module-groups.yaml')
    config.save(output_path)

    # 요약 출력
    print(f"\n[group-cli] ✅ Saved {len(config.modules)} modules:")
    for m in config.modules:
        print(f"  - {m.name}: {len(m.files)} files")

    total_files = len(config.get_all_files())
    print(f"\n  Total unique files: {total_files}")
    print(f"  Output: {output_path}")

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """설정 파일 유효성 검사."""
    print("[group-cli] Validating config...")

    config = load_config(args.config)
    errors = validate_config(config)

    if errors:
        print("[group-cli] ❌ Validation failed:")
        for err in errors:
            print(f"    - {err}")
        return 1
    else:
        print("[group-cli] ✅ Config is valid!")
        print(f"  Modules: {len(config.modules)}")
        print(f"  Total files: {len(config.get_all_files())}")
        return 0


def cmd_list(args: argparse.Namespace) -> int:
    """모듈 목록 출력."""
    config = load_config(args.config)

    print(f"[group-cli] Module Groups ({len(config.modules)} modules):")
    print()

    for m in config.modules:
        print(f"📦 {m.name}")
        print(f"   Files: {len(m.files)}")
        if m.rationale:
            print(f"   Rationale: {m.rationale[:80]}...")
        if m.hitl_review:
            print(f"   HITL: {m.hitl_review}")
        print()

    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI 진입점."""
    parser = argparse.ArgumentParser(
        prog='group-cli',
        description='HITL Module Grouping CLI'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # discover 명령
    p_discover = subparsers.add_parser('discover', help='Run LLM Module Discovery')
    p_discover.add_argument('--ast-dir', required=True, help='AST graph directory')
    p_discover.add_argument('--output-dir', required=True, help='Output directory')
    p_discover.add_argument('--prompt', default='A', choices=['A', 'B'], help='Prompt template')
    p_discover.add_argument('--strategy', default='flat', choices=['flat'], help='Discovery strategy')
    p_discover.add_argument(
        '--prompt-file-limit',
        type=int,
        default=1000,
        help='Max files to list before large-repo prompt mode; 0 lists all files',
    )
    p_discover.add_argument(
        '--large-repo-mode',
        default='auto',
        choices=['auto', 'hierarchy', 'semantic'],
        help='Prompt mode when the file limit is reached: auto/hierarchy uses directory hierarchy, semantic keeps legacy directory-summary review',
    )
    p_discover.add_argument(
        '--hierarchy-max-modules',
        type=int,
        default=100,
        help='Maximum target module count for logical-hierarchy prompts',
    )
    p_discover.set_defaults(func=cmd_discover)

    # review 명령
    p_review = subparsers.add_parser('review', help='Review LLM response')
    p_review.add_argument('--ast-dir', required=True, help='AST graph directory')
    p_review.add_argument('--output-dir', required=True, help='Output directory')
    p_review.add_argument('--llm-response', required=True, help='LLM response file')
    p_review.add_argument('--output', help='Output file name')
    p_review.add_argument('--allow-broad-patterns', action='store_true', help='Allow broad include patterns such as src/**')
    p_review.set_defaults(func=cmd_review)

    # save 명령
    p_save = subparsers.add_parser('save', help='Save final module groups')
    p_save.add_argument('--config', required=True, help='Config file to save')
    p_save.add_argument('--output-dir', required=True, help='Output directory')
    p_save.add_argument('--force', action='store_true', help='Force save despite errors')
    p_save.set_defaults(func=cmd_save)

    # validate 명령
    p_validate = subparsers.add_parser('validate', help='Validate config file')
    p_validate.add_argument('--config', required=True, help='Config file to validate')
    p_validate.set_defaults(func=cmd_validate)

    # list 명령
    p_list = subparsers.add_parser('list', help='List module groups')
    p_list.add_argument('--config', required=True, help='Config file to list')
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
