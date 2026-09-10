#!/usr/bin/env python3
"""Runtime stats and history commands for Code2Spec runs."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

try:
    from .common import (
        CODE2SPEC_VERSION,
        HISTORY_FILE,
        PROJECT_HISTORY_DETAILS_HEADING,
        PROJECT_HISTORY_FORMAT_VERSION,
        PROJECT_HISTORY_HEADER,
        PROJECT_HISTORY_NOTE,
        PROJECT_HISTORY_SEPARATOR,
        PROJECT_HISTORY_SUMMARY_HEADING,
        _format_duration,
        _load_json,
        _load_runtime_stats,
        _resolve_spec_root,
        _save_runtime_stats,
    )
    from .state import _load
except ImportError:  # script/installed-tools flat execution
    from progress.common import (
        CODE2SPEC_VERSION,
        HISTORY_FILE,
        PROJECT_HISTORY_DETAILS_HEADING,
        PROJECT_HISTORY_FORMAT_VERSION,
        PROJECT_HISTORY_HEADER,
        PROJECT_HISTORY_NOTE,
        PROJECT_HISTORY_SEPARATOR,
        PROJECT_HISTORY_SUMMARY_HEADING,
        _format_duration,
        _load_json,
        _load_runtime_stats,
        _resolve_spec_root,
        _save_runtime_stats,
    )
    from progress.state import _load

try:
    from ..analysis_paths import get_canonical_paths
    from ..quality_metrics import load_quality_metrics
except ImportError:  # script/installed-tools flat execution
    from analysis_paths import get_canonical_paths
    from quality_metrics import load_quality_metrics

try:
    from .telemetry import (
        append_telemetry_event,
        load_run_config,
        resolve_git_context,
        resolve_run_context,
        update_runtime_telemetry,
    )
except ImportError:  # script/installed-tools flat execution
    from progress.telemetry import (
        append_telemetry_event,
        load_run_config,
        resolve_git_context,
        resolve_run_context,
        update_runtime_telemetry,
    )

PROJECT_HISTORY_METRICS_HEADING = "## 품질 메트릭"
PROJECT_HISTORY_METRICS_HEADER = (
    "| 실행 일시 | Spec 경로 | 유형 | 모드 | Evidence Precision | "
    "Source Coverage | Core Coverage | Broken Source Link Rate | Quality Gate |"
)
PROJECT_HISTORY_METRICS_SEPARATOR = "|---|---|---|---|---:|---:|---:|---:|---|"


def _init_runtime_stats(
    output_dir: Path,
    session_id: str,
    target_path: str,
    mode: str,
    code_size: dict,
    version: str = CODE2SPEC_VERSION,
    run_type: str = "full",
    workspace_root: str = "",
    analysis_target: str = "",
    output_root: str = "",
    analysis_scope: int | None = None,
    git_context: dict | None = None,
    coding_agent: str = "",
) -> dict:
    """runtime-stats.json 초기화."""
    workflow_names = ["W-DELTA"] if run_type == "delta" else ["W1", "W2", "W3"]
    data = {
        "code2spec_version": version,
        "session_id": session_id,
        "run_type": run_type,
        "mode": mode,  # light, standard, detail
        "target_path": target_path,
        "workspace_root": workspace_root,
        "analysis_target": analysis_target,
        "output_root": output_root,
        "code_size": code_size,
        "workflows": {
            workflow: {
                "start_time": None,
                "end_time": None,
                "duration_seconds": 0,
                "token_usage": 0,
                "coding_agent": None,
            }
            for workflow in workflow_names
        },
        "total_duration_seconds": 0,
        "total_token_usage": 0,
        "telemetry": {
            "version": "1.0",
            "events_file": "telemetry-events.jsonl",
            "event_count": 0,
            "workflow_usage": {
                "total_runs": 0,
                "by_workflow": {
                    workflow: {
                        "started": 0,
                        "completed": 0,
                        "in_progress": 0,
                        "failed": 0,
                        "attempt_count": 0,
                        "completed_once": False,
                    }
                    for workflow in workflow_names
                },
            },
            "latest_event": None,
            "latest_progress_event": None,
            "latest_failure": None,
            "token_usage": {"status": "unknown", "total": 0},
        },
    }
    if analysis_scope is not None:
        data["analysis_scope"] = analysis_scope
        data["telemetry"]["analysis_scope"] = analysis_scope
    if git_context:
        data["git"] = git_context
        data["telemetry"]["git"] = git_context
    if coding_agent:
        data["coding_agent"] = coding_agent
    _save_runtime_stats(output_dir, data)
    return data


def _normalize_workflow_name(workflow: str) -> str:
    return workflow.upper()


def _coding_agent_from_args(args: argparse.Namespace) -> str:
    return str(getattr(args, "coding_agent", "") or "").strip()


def _coding_agents_for_history(stats: dict) -> list[str]:
    agents: list[str] = []
    for workflow in stats.get("workflows", {}).values():
        agent = workflow.get("coding_agent") if isinstance(workflow, dict) else None
        if isinstance(agent, str) and agent and agent not in agents:
            agents.append(agent)
    current = stats.get("coding_agent")
    if isinstance(current, str) and current and current not in agents:
        agents.append(current)
    return agents


def _workflow_names_for_history(stats: dict) -> list[str]:
    workflows = stats.get("workflows", {})
    if workflows:
        return list(workflows.keys())
    if stats.get("run_type") == "delta":
        return ["W-DELTA"]
    return ["W1", "W2", "W3"]


def _workflow_duration_summary(stats: dict) -> str:
    workflows = stats.get("workflows", {})
    parts = []
    for name in _workflow_names_for_history(stats):
        duration = _format_duration(workflows.get(name, {}).get("duration_seconds", 0))
        parts.append(f"{name} {duration}")
    return " / ".join(parts) if parts else "-"


def _workflow_duration_pairs(stats: dict) -> list[tuple[str, str]]:
    workflows = stats.get("workflows", {})
    pairs: list[tuple[str, str]] = []
    for name in _workflow_names_for_history(stats):
        duration = _format_duration(workflows.get(name, {}).get("duration_seconds", 0))
        pairs.append((name, duration))
    return pairs


def _sanitize_history_cell(value: object) -> str:
    text = str(value if value is not None else "-").replace("\n", " ").strip()
    return text.replace("|", "\\|") or "-"


def _format_history_datetime(session_id: object) -> str:
    """Format history session ids as human-readable datetimes.

    Accepts current ids such as ``20260414_010203`` and legacy table values such as
    ``20260414 010203``. Unknown values are returned as-is so history generation
    remains tolerant of hand-edited files.
    """
    text = str(session_id or "?").strip()
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 14:
        return (
            f"{digits[:4]}-{digits[4:6]}-{digits[6:8]} "
            f"{digits[8:10]}:{digits[10:12]}:{digits[12:14]}"
        )
    return text or "?"


def _default_code_size() -> dict:
    return {
        "total_files": 0,
        "total_lines": 0,
        "total_bytes": 0,
        "by_extension": {},
        "filters": {"min_lines": 0},
    }


def _parse_code_size(args: argparse.Namespace) -> dict:
    target_path_value = (
        getattr(args, "analysis_target", "") or getattr(args, "target_path", "")
    )
    if target_path_value:
        target_path = Path(target_path_value)
        if target_path.exists():
            try:
                from ..exporter import get_code_size
            except ImportError:  # script/installed-tools flat execution
                from exporter import get_code_size

            measured = get_code_size(target_path)
            code_size = _default_code_size()
            code_size["total_files"] = measured.total_files
            code_size["total_lines"] = measured.total_lines
            code_size["total_bytes"] = measured.total_bytes
            code_size["by_extension"] = measured.by_extension
            return code_size

    return _default_code_size()


def _code_size_min_lines(code_size: dict) -> int:
    filters = code_size.get("filters", {})
    if isinstance(filters, dict):
        min_lines = filters.get("min_lines", 0)
        if isinstance(min_lines, int):
            return min_lines
    return 0


def _code_size_telemetry_payload(code_size: dict) -> dict:
    """Return code-size fields suitable for telemetry event payloads."""
    payload = {
        "code_size": code_size,
        "code_size_total_files": code_size.get("total_files", 0),
        "code_size_total_lines": code_size.get("total_lines", 0),
        "code_size_total_bytes": code_size.get("total_bytes", 0),
        "code_size_by_extension": code_size.get("by_extension", {}),
        "code_size_filters": code_size.get("filters", {}),
    }
    for source_key, telemetry_key in (
        ("classes", "code_size_classes"),
        ("functions", "code_size_functions"),
        ("ast_nodes", "code_size_ast_nodes"),
    ):
        if source_key in code_size:
            payload[telemetry_key] = code_size.get(source_key, 0)
    return payload


def _load_ast_node_stats(output_dir: Path) -> dict | None:
    """Load aggregate AST node counts from the code-to-ast raw graph."""
    candidates = [
        get_canonical_paths(output_dir).ast_output_dir / "graph-raw.json",
        output_dir / "graph-raw.json",
    ]
    graph_path = next((path for path in candidates if path.exists()), None)
    if graph_path is None:
        return None

    try:
        data = json.loads(graph_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None

    if not isinstance(data, dict):
        return None

    nodes = data.get("nodes", [])
    if not isinstance(nodes, list):
        return None

    counts = {"classes": 0, "functions": 0}
    total_nodes = 0
    for node in nodes:
        if not isinstance(node, dict):
            continue
        total_nodes += 1
        kind = node.get("kind")
        if kind == "Class":
            counts["classes"] += 1
        elif kind == "Function":
            counts["functions"] += 1

    counts["total_nodes"] = total_nodes
    return counts


def _store_ast_stats_in_code_size(
    output_dir: Path,
    stats: dict,
    ast_stats: dict | None,
) -> None:
    """Store AST-derived code-size metrics in runtime-stats.json."""
    if ast_stats is None:
        return

    code_size = stats.get("code_size")
    if not isinstance(code_size, dict):
        code_size = _default_code_size()
        stats["code_size"] = code_size

    code_size["classes"] = ast_stats.get("classes", 0)
    code_size["functions"] = ast_stats.get("functions", 0)
    code_size["ast_nodes"] = ast_stats.get("total_nodes", 0)
    _save_runtime_stats(output_dir, stats)


def _format_code_size_summary(code_size: dict) -> str:
    summary = (
        f"{code_size.get('total_files', 0)}파일 / "
        f"{code_size.get('total_lines', 0):,}행"
    )
    if "functions" not in code_size and "classes" not in code_size:
        return summary

    summary += (
        f" / {code_size.get('functions', 0):,}함수"
        f" / {code_size.get('classes', 0):,}클래스"
    )
    return summary


def cmd_session_init(args: argparse.Namespace) -> None:
    """code2spec 세션 초기화 - runtime-stats.json 생성."""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    code_size = _parse_code_size(args)
    target_path = args.target_path or ""
    workspace_root = getattr(args, "workspace_root", "") or target_path
    analysis_target = getattr(args, "analysis_target", "") or target_path
    output_root = getattr(args, "output_root", "") or str(_resolve_spec_root(output_dir))
    run_context = resolve_run_context({}, load_run_config(output_dir))
    coding_agent = _coding_agent_from_args(args)
    git_context = resolve_git_context(
        output_dir,
        {
            "target_path": target_path,
            "workspace_root": workspace_root,
            "analysis_target": analysis_target,
        },
    )

    data = _init_runtime_stats(
        output_dir=output_dir,
        session_id=session_id,
        target_path=target_path,
        mode=args.mode or "detail",  # Physical 모드 제거 이후 항상 detail
        code_size=code_size,
        version=CODE2SPEC_VERSION,
        run_type=getattr(args, "run_type", "full") or "full",
        workspace_root=workspace_root,
        analysis_target=analysis_target,
        output_root=output_root,
        analysis_scope=run_context.get("analysis_scope"),
        git_context=git_context,
        coding_agent=coding_agent,
    )

    print(f"[ProgressTracker] Session initialized: {session_id}")
    print(f"  Run type: {data['run_type']}")
    print(f"  Mode: {data['mode']}")
    if coding_agent:
        print(f"  Coding assistant: {coding_agent}")
    if isinstance(data.get("git"), dict) and data["git"].get("repo"):
        git_ref = data["git"].get("branch") or str(data["git"].get("commit", ""))[:12] or "unknown"
        print(f"  Git: {data['git']['repo']} @ {git_ref}")
    print(f"  Target: {data['target_path']}")
    if data.get("analysis_target") and data["analysis_target"] != data["target_path"]:
        print(f"  Analysis target: {data['analysis_target']}")
    if data.get("output_root"):
        print(f"  Output root: {data['output_root']}")
    print(
        f"  Code size: {code_size['total_files']} files, {code_size['total_lines']} lines"
    )
    print(f"  Min lines: {code_size['filters']['min_lines']}")
    print(f"  → {get_canonical_paths(output_dir).runtime_stats}")
    session_payload = {
        "target_path": target_path,
        "workspace_root": workspace_root,
        "analysis_target": analysis_target,
        "output_root": output_root,
    }
    session_payload.update(_code_size_telemetry_payload(code_size))
    append_telemetry_event(
        output_dir,
        "session_started",
        payload=session_payload,
    )
    append_telemetry_event(
        output_dir,
        "code_size_measured",
        payload=_code_size_telemetry_payload(code_size),
    )


def cmd_workflow_start(args: argparse.Namespace) -> None:
    """워크플로우 시작 시간 기록."""
    output_dir = Path(args.output_dir)
    stats = _load_runtime_stats(output_dir)
    if not stats:
        print("[ERROR] No runtime-stats.json found. Run 'session-init' first.")
        return

    workflow = _normalize_workflow_name(args.workflow)
    if workflow not in stats.get("workflows", {}):
        print(f"[ERROR] Invalid workflow: {workflow}")
        return

    coding_agent = _coding_agent_from_args(args)
    if coding_agent:
        stats["coding_agent"] = coding_agent
        stats["workflows"][workflow]["coding_agent"] = coding_agent
    stats["workflows"][workflow]["start_time"] = datetime.now().isoformat(
        timespec="seconds"
    )
    _save_runtime_stats(output_dir, stats)
    append_telemetry_event(output_dir, "workflow_started", workflow=workflow)
    print(
        f"[ProgressTracker] {workflow} started at {stats['workflows'][workflow]['start_time']}"
    )


def cmd_workflow_end(args: argparse.Namespace) -> None:
    """워크플로우 종료 시간 기록."""
    output_dir = Path(args.output_dir)
    stats = _load_runtime_stats(output_dir)
    if not stats:
        print("[ERROR] No runtime-stats.json found. Run 'session-init' first.")
        return

    workflow = _normalize_workflow_name(args.workflow)
    if workflow not in stats.get("workflows", {}):
        print(f"[ERROR] Invalid workflow: {workflow}")
        return

    end_time = datetime.now()
    start_time_str = stats["workflows"][workflow].get("start_time")

    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str)
        duration_seconds = int((end_time - start_time).total_seconds())
    else:
        duration_seconds = 0

    token_usage = 0

    coding_agent = _coding_agent_from_args(args)
    if coding_agent:
        stats["coding_agent"] = coding_agent
        stats["workflows"][workflow]["coding_agent"] = coding_agent
    stats["workflows"][workflow]["end_time"] = end_time.isoformat(timespec="seconds")
    stats["workflows"][workflow]["duration_seconds"] = duration_seconds
    stats["workflows"][workflow]["token_usage"] = token_usage

    # 총계 업데이트
    stats["total_duration_seconds"] = sum(
        w.get("duration_seconds", 0) for w in stats["workflows"].values()
    )
    stats["total_token_usage"] = sum(
        w.get("token_usage", 0) for w in stats["workflows"].values()
    )

    _save_runtime_stats(output_dir, stats)
    append_telemetry_event(
        output_dir,
        "workflow_completed",
        workflow=workflow,
        payload={
            "duration_seconds": duration_seconds,
            "token_usage": token_usage,
        },
    )

    duration_str = _format_duration(duration_seconds)
    print(f"[ProgressTracker] {workflow} completed:")
    print(f"  Duration: {duration_str}")


def cmd_finalize_history(args: argparse.Namespace) -> None:
    """history.md 파일 생성 (프로젝트 전체 + 세션별)."""
    output_dir = Path(args.output_dir)
    stats = _load_runtime_stats(output_dir)
    if not stats:
        print("[ERROR] No runtime-stats.json found.")
        return

    progress = _load(output_dir)
    module_count = progress.get("total_modules", 0)
    completed_count = len(progress.get("completed", []))

    # MD 파일 수 계산
    spec_root = _resolve_spec_root(output_dir)
    md_count, md_lines = _collect_markdown_stats(spec_root)

    # 세션별 history.md 생성
    updated_specs = _updated_specs_for_history(output_dir, progress)
    ast_stats = _load_ast_node_stats(output_dir)
    _store_ast_stats_in_code_size(output_dir, stats, ast_stats)
    append_telemetry_event(
        output_dir,
        "code_size_finalized",
        payload=_code_size_telemetry_payload(stats.get("code_size", {})),
    )

    append_telemetry_event(
        output_dir,
        "history_finalized",
        payload={
            "md_count": md_count,
            "md_lines": md_lines,
            "module_count": module_count,
            "completed_count": completed_count,
        },
    )
    stats = _load_runtime_stats(output_dir) or stats
    update_runtime_telemetry(output_dir)
    stats = _load_runtime_stats(output_dir) or stats

    _create_session_history(
        output_dir,
        stats,
        module_count,
        completed_count,
        md_count,
        md_lines,
        args.note,
        updated_specs,
    )

    # 프로젝트 전체 history.md 업데이트
    project_root = spec_root
    _update_project_history(
        project_root,
        stats,
        module_count,
        md_count,
        md_lines,
        args.note,
        updated_specs,
    )

    print("[ProgressTracker] History updated:")
    print(f"  Session: {output_dir / HISTORY_FILE}")
    print(f"  Project: {project_root / HISTORY_FILE}")


def _create_session_history(
    output_dir: Path,
    stats: dict,
    module_count: int,
    completed_count: int,
    md_count: int,
    md_lines: int,
    note: str,
    updated_specs: list[dict],
) -> None:
    """세션별 상세 history.md 생성."""
    lines = [
        "# Code2Spec Session History",
        "",
        "## 세션 정보",
        "",
        f"- **실행 일시**: {_format_history_datetime(stats.get('session_id', '?'))}",
        f"- **code2spec 버전**: {stats.get('code2spec_version', '?')}",
        f"- **실행 유형**: {stats.get('run_type', 'full')}",
        f"- **Coding assistants**: {', '.join(_coding_agents_for_history(stats)) or '-'}",
        f"- **History format**: {PROJECT_HISTORY_FORMAT_VERSION}",
        f"- **분석 모드**: {stats.get('mode', '?').capitalize()}",
        f"- **분석 대상**: `{stats.get('target_path', '?')}`",
        "",
        "## 코드 규모",
        "",
    ]

    code_size = stats.get("code_size", {})
    lines.append(f"- 총 파일 수: {code_size.get('total_files', 0):,}개")
    lines.append(f"- 총 라인 수: {code_size.get('total_lines', 0):,}행")
    if "classes" in code_size or "functions" in code_size:
        lines.append(f"- 클래스 수: {code_size.get('classes', 0):,}개")
        lines.append(f"- 함수 수: {code_size.get('functions', 0):,}개")
    lines.append(
        f"- 총 용량: {code_size.get('total_bytes', 0):,} bytes ({code_size.get('total_bytes', 0) / 1024:.1f} KB)"
    )
    lines.append(
        "- 기준: AST 파싱된 소스 파일 기준 "
        f"(hidden dot 경로 제외, min_lines={_code_size_min_lines(code_size)})"
    )
    lines.append("")

    # 확장자별 통계
    by_ext = code_size.get("by_extension", {})
    if by_ext:
        lines.append("### 확장자별 통계")
        lines.append("")
        lines.append("| 확장자 | 파일 수 | 라인 수 | 용량 |")
        lines.append("|--------|--------|---------|------|")
        for ext, ext_stats in sorted(
            by_ext.items(), key=lambda x: x[1]["lines"], reverse=True
        ):
            lines.append(
                f"| {ext} | {ext_stats['files']:,} | {ext_stats['lines']:,} | {ext_stats['bytes']:,} |"
            )
        lines.append("")

    # 워크플로우별 상세
    lines.append("## 워크플로우별 상세")
    lines.append("")
    lines.append("| Workflow | 시작 | 종료 | 소요시간 | 상태 |")
    lines.append("|----------|------|------|----------|------|")

    workflows = stats.get("workflows", {})
    for wf in _workflow_names_for_history(stats):
        wf_data = workflows.get(wf, {})
        start = wf_data.get("start_time", "-")
        end = wf_data.get("end_time", "-")
        duration = _format_duration(wf_data.get("duration_seconds", 0))
        status = "✅" if wf_data.get("end_time") else "⏳"
        lines.append(
            f"| {wf} | {start[11:19] if start else '-'} | "
            f"{end[11:19] if end else '-'} | {duration} | {status} |"
        )

    # 총계
    total_duration = _format_duration(stats.get("total_duration_seconds", 0))
    lines.append(f"| **총계** | | | **{total_duration}** | |")
    lines.append("")

    workflow_agents = [
        (wf, workflows.get(wf, {}).get("coding_agent"))
        for wf in _workflow_names_for_history(stats)
        if workflows.get(wf, {}).get("coding_agent")
    ]
    if workflow_agents:
        lines.append("### Workflow coding assistants")
        lines.append("")
        lines.append("| Workflow | Coding Assistant |")
        lines.append("|----------|------------------|")
        for workflow, coding_agent in workflow_agents:
            lines.append(f"| {workflow} | {coding_agent} |")
        lines.append("")

    _append_telemetry_summary(lines, stats)

    # 결과물 요약
    lines.append("## 결과물 요약")
    lines.append("")
    lines.append(f"- 모듈 수: {completed_count}/{module_count}")
    lines.append(f"- MD 파일: {md_count}개")
    lines.append(f"- MD 총 라인 수: {md_lines:,}행")
    lines.append(f"- 비고: {note or '-'}")
    # 품질 메트릭 섹션
    try:
        from ..analysis_paths import get_canonical_paths
    except ImportError:
        from analysis_paths import get_canonical_paths
    _paths = get_canonical_paths(output_dir)
    metrics = load_quality_metrics(_paths.quality_metrics)
    if metrics is not None:
        lines.append("")
        lines.append("## 품질 메트릭")
        lines.append("")
        lines.append("| 메트릭 | 값 | 세부 |")
        lines.append("|--------|------|------|")
        lines.append(
            f"| Evidence Precision | {metrics.evidence_precision:.2%} | "
            f"{metrics.valid_source_tags}/{metrics.total_source_tags} 태그 유효 |"
        )
        lines.append(
            f"| Source Coverage | {metrics.source_coverage:.2%} | "
            f"{metrics.referenced_source_files}/{metrics.total_source_files} 파일 참조 |"
        )
        if getattr(metrics, "core_coverage_unit", "file") == "module":
            core_detail = (
                f"{metrics.referenced_core_modules}/{metrics.total_core_modules} "
                "Core 모듈 카드 생성"
            )
        else:
            core_detail = (
                f"{metrics.referenced_core_files}/{metrics.total_core_files} "
                "Core 파일 참조"
            )
        lines.append(
            f"| Core Coverage | {metrics.core_coverage:.2%} | {core_detail} |"
        )
        lines.append(
            f"| Broken Source Link Rate | {metrics.broken_source_link_rate:.2%} | "
            f"{metrics.broken_source_links}/{metrics.total_source_links} 링크 깨짐 |"
        )

        quality_issues = _load_json(_paths.quality_issues)
        if quality_issues:
            status = quality_issues.get("status", "-")
            issue_count = len(quality_issues.get("issues", []))
            lines.append(
                f"| Quality Gate | {status} | "
                f"{issue_count} issues (`.analysis/reports/quality/quality-issues.json`) |"
            )
        lines.append("")

    if updated_specs:
        lines.append("")
        lines.append("## 갱신된 Spec")
        lines.append("")
        lines.append("| Source | Overview | SDD | FR |")
        lines.append("|--------|----------|-----|----|")
        for spec in updated_specs:
            lines.append(
                _updated_spec_table_row(
                    spec,
                    base_dir=output_dir,
                    spec_root=_resolve_spec_root(output_dir),
                )
            )

    (output_dir / HISTORY_FILE).write_text("\n".join(lines) + "\n", encoding="utf-8")



def _append_telemetry_summary(lines: list[str], stats: dict) -> None:
    telemetry = stats.get("telemetry")
    if not isinstance(telemetry, dict):
        return

    lines.append("## Telemetry 요약")
    lines.append("")
    lines.append(f"- 이벤트 파일: `{telemetry.get('events_file', 'telemetry-events.jsonl')}`")
    lines.append(f"- 이벤트 수: {telemetry.get('event_count', 0):,}개")
    coding_agents = telemetry.get("coding_agents", [])
    if isinstance(coding_agents, list) and coding_agents:
        lines.append(f"- Coding assistants: {', '.join(map(str, coding_agents))}")
    git_context = telemetry.get("git") if isinstance(telemetry.get("git"), dict) else stats.get("git")
    if isinstance(git_context, dict) and git_context.get("repo"):
        git_ref = git_context.get("branch") or str(git_context.get("commit", ""))[:12] or "unknown"
        lines.append(f"- Git repo: `{git_context.get('repo')}` @ `{git_ref}`")

    token_usage = telemetry.get("token_usage") if isinstance(telemetry.get("token_usage"), dict) else {}
    token_status = token_usage.get("status", "unknown")
    token_total = token_usage.get("total")
    if token_status == "measured" and isinstance(token_total, int):
        lines.append(f"- Token 사용량: {token_total:,} tokens")
    else:
        lines.append("- Token 사용량: unknown (provider token source 미연동)")

    workflow_usage = telemetry.get("workflow_usage") if isinstance(telemetry.get("workflow_usage"), dict) else {}
    by_workflow = workflow_usage.get("by_workflow") if isinstance(workflow_usage.get("by_workflow"), dict) else {}
    if by_workflow:
        lines.append("")
        lines.append("### Workflow 사용 횟수")
        lines.append("")
        lines.append("| Workflow | Started | Completed | In Progress | Failed | Attempts |")
        lines.append("|----------|--------:|----------:|------------:|-------:|---------:|")
        for workflow, counts in by_workflow.items():
            if not isinstance(counts, dict):
                continue
            started = counts.get("started", 0)
            completed = counts.get("completed", 0)
            in_progress = counts.get("in_progress", 0)
            failed = counts.get("failed", 0)
            attempts = counts.get("attempt_count", 0)
            if not any([started, completed, in_progress, failed, attempts]):
                continue
            lines.append(
                f"| {workflow} | {started:,} | {completed:,} | {in_progress:,} | {failed:,} | {attempts:,} |"
            )

    latest_failure = telemetry.get("latest_failure")
    if isinstance(latest_failure, dict) and latest_failure:
        lines.append("")
        lines.append("### 최근 실패 상태")
        lines.append("")
        lines.append(f"- Workflow: {latest_failure.get('workflow', '-')}")
        lines.append(f"- Step: {latest_failure.get('step', '-')}")
        lines.append(f"- Reason: {latest_failure.get('reason_category', 'unknown')}")
        lines.append(f"- Message: {latest_failure.get('message', '-') or '-'}")
    lines.append("")

def _updated_specs_for_history(output_dir: Path, progress: dict) -> list[dict]:
    """Return source→spec document rows for the current delta run."""
    if not progress.get("delta"):
        return []

    diff_plan_path = progress.get("diff_plan_path")
    if not diff_plan_path:
        return []

    path = Path(diff_plan_path)
    if not path.exists():
        # analysis-progress.json stores absolute paths in current flows, but keep a
        # relative fallback for hand-edited or legacy progress files.
        path = output_dir / diff_plan_path
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return []

    cache_docs = _spec_cache_docs_by_source(output_dir)
    rows: list[dict] = []
    for bucket in (
        "changed_modules",
        "new_modules",
        "promoted_modules",
        "dependent_changed_modules",
    ):
        for item in data.get(bucket, []):
            if not isinstance(item, dict):
                continue
            source = item.get("file")
            if not source:
                continue
            docs = cache_docs.get(_history_source_key(source), {})
            rows.append(
                _updated_spec_row(
                    source=source,
                    sdd_doc=item.get("sdd_doc") or docs.get("sdd_doc") or "-",
                    fr_doc=item.get("fr_doc") or docs.get("fr_doc") or "-",
                    overview=item.get("overview")
                    or _updated_spec_overview(bucket, item),
                )
            )

    for item in data.get("moved_modules", []):
        if not isinstance(item, dict):
            continue
        source = item.get("to") or item.get("file")
        if not source:
            continue
        docs = cache_docs.get(_history_source_key(source), {})
        rows.append(
            _updated_spec_row(
                source=source,
                sdd_doc=item.get("sdd_doc") or docs.get("sdd_doc") or "-",
                fr_doc=item.get("fr_doc") or docs.get("fr_doc") or "-",
                overview=item.get("overview")
                or _updated_spec_overview("moved_modules", item),
            )
        )

    return _dedupe_updated_spec_rows(rows)


def _updated_spec_row(
    *,
    source: str,
    sdd_doc: str,
    fr_doc: str,
    overview: str,
) -> dict:
    return {
        "source": _history_relative_path(source),
        "source_path": _history_source_key(source),
        "sdd_doc": sdd_doc,
        "fr_doc": fr_doc,
        "overview": overview,
    }


def _updated_spec_overview(bucket: str, item: dict) -> str:
    if bucket == "changed_modules":
        return "소스 변경으로 기존 SDD/FR 갱신"
    if bucket == "new_modules":
        return "신규 소스 기준 spec 생성"
    if bucket == "promoted_modules":
        return "Core 승격으로 spec 생성/갱신"
    if bucket == "dependent_changed_modules":
        changed_dep = item.get("changed_dep")
        if changed_dep:
            return (
                f"참조 소스 변경({_history_relative_path(changed_dep)})으로 "
                "의존 spec 갱신"
            )
        return "참조 소스 변경으로 의존 spec 갱신"
    if bucket == "moved_modules":
        from_path = item.get("from")
        if from_path:
            return f"파일 이동({_history_relative_path(from_path)} → 현재 경로) 반영"
        return "파일 이동을 새 경로 기준으로 반영"
    return "Delta spec 갱신"


def _spec_cache_docs_by_source(output_dir: Path) -> dict[str, dict]:
    try:
        try:
            from ..delta.spec_cache import load_spec_cache
        except ImportError:  # script/installed-tools flat execution
            from delta.spec_cache import load_spec_cache
    except ImportError:
        return {}

    try:
        try:
            from ..analysis_paths import get_canonical_paths
        except ImportError:
            from analysis_paths import get_canonical_paths
        _cache_paths = get_canonical_paths(output_dir)
        cache = load_spec_cache(_cache_paths.spec_cache)
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    if not cache:
        return {}

    return {
        _history_source_key(entry.file_path): {
            "sdd_doc": entry.sdd_doc,
            "fr_doc": entry.fr_doc,
        }
        for entry in cache.entries.values()
    }


def _history_source_key(path: str) -> str:
    try:
        return str(Path(path).resolve())
    except OSError:
        return path


def _history_relative_path(path: str) -> str:
    try:
        return str(Path(path).resolve().relative_to(Path.cwd().resolve()))
    except (OSError, ValueError):
        return path


def _dedupe_updated_spec_rows(rows: list[dict]) -> list[dict]:
    deduped: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (
            str(row.get("source", "")),
            str(row.get("sdd_doc", "")),
            str(row.get("fr_doc", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def _updated_spec_table_row(spec: dict, *, base_dir: Path, spec_root: Path) -> str:
    source = _history_link_cell(
        spec.get("source", "-"), spec.get("source_path", ""), base_dir
    )
    overview = _sanitize_history_cell(spec.get("overview", "-"))
    sdd = _history_doc_link_cell(spec.get("sdd_doc", "-"), base_dir, spec_root)
    fr = _history_doc_link_cell(spec.get("fr_doc", "-"), base_dir, spec_root)
    return f"| {source} | {overview} | {sdd} | {fr} |"


def _history_doc_link_cell(doc: str, base_dir: Path, spec_root: Path) -> str:
    if not doc or doc == "-":
        return "-"
    return _history_link_cell(doc, str(spec_root / doc), base_dir)


def _history_link_cell(label: str, target: str, base_dir: Path) -> str:
    if not label or label == "-":
        return "-"
    if not target:
        return _sanitize_history_cell(label)
    try:
        rel = os.path.relpath(Path(target).resolve(), base_dir.resolve())
        href = Path(rel).as_posix().replace(" ", "%20")
    except (OSError, ValueError):
        href = target.replace(" ", "%20")
    return f"[{_sanitize_history_cell(label)}]({_sanitize_history_cell(href)})"


def _update_project_history(
    project_root: Path,
    stats: dict,
    module_count: int,
    md_count: int,
    md_lines: int,
    note: str,
    updated_specs: list[dict],
) -> None:
    """프로젝트 전체 history.md 업데이트 (요약 + 워크플로우 상세 형태)."""
    history_path = project_root / HISTORY_FILE

    if history_path.exists():
        content = history_path.read_text(encoding="utf-8")
    else:
        content = ""

    summary_rows, metric_rows, detail_blocks, legacy_notes = (
        _normalize_project_history_content(content)
    )
    record = _project_history_record_from_stats(
        project_root,
        stats,
        module_count,
        md_count,
        md_lines,
        note,
        updated_specs,
    )
    current_key = _project_history_record_key(record)
    summary_rows = [
        row
        for row in summary_rows
        if not _project_history_keys_match(
            _project_history_summary_row_key(row), current_key
        )
    ]
    metric_rows = [
        row
        for row in metric_rows
        if not _project_history_keys_match(
            _project_history_metric_row_key(row), current_key
        )
    ]
    detail_blocks = [
        block
        for block in detail_blocks
        if not _project_history_keys_match(
            _project_history_detail_block_key(block), current_key
        )
    ]

    current_metric_row = _project_history_metric_row(record)
    content = _render_project_history_content(
        [_project_history_summary_row(record), *summary_rows],
        ([current_metric_row] if current_metric_row else []) + metric_rows,
        [_project_history_detail_block(record), *detail_blocks],
        legacy_notes,
    )
    history_path.write_text(content, encoding="utf-8")


def _project_history_record_from_stats(
    project_root: Path,
    stats: dict,
    module_count: int,
    md_count: int,
    md_lines: int,
    note: str,
    updated_specs: list[dict],
) -> dict:
    code_size = stats.get("code_size", {})

    # 품질 메트릭 로드
    analysis_dir = Path(project_root) / ".analysis"
    try:
        from ..analysis_paths import get_canonical_paths as _get_paths
    except ImportError:
        from analysis_paths import get_canonical_paths as _get_paths
    _hist_paths = _get_paths(analysis_dir)
    metrics = load_quality_metrics(_hist_paths.quality_metrics)

    return {
        "project_root": str(project_root),
        "date_time": _format_history_datetime(stats.get("session_id", "?")),
        "spec_path": f"{project_root.name}/",
        "version": stats.get("code2spec_version", "?"),
        "run_type": stats.get("run_type", "full"),
        "mode": stats.get("mode", "?").capitalize(),
        "module_count": str(module_count),
        "code_size": _format_code_size_summary(code_size),
        "workflows": _workflow_duration_pairs(stats),
        "total_duration": _format_duration(stats.get("total_duration_seconds", 0)),
        "md_summary": f"{md_count}개 / {md_lines:,}행",
        "note": note or "-",
        "coding_agents": _coding_agents_for_history(stats),
        "updated_specs": updated_specs,
        # 품질 메트릭 / gate 결과 (Summary 아래 별도 섹션에서 렌더링)
        "quality_metrics": metrics,
        "quality_issues": _load_json(_hist_paths.quality_issues),
    }


def _project_history_record_key(record: dict) -> tuple[str, str, str, str]:
    return (
        str(record.get("date_time", "?")),
        str(record.get("spec_path", "?")),
        str(record.get("run_type", "full")),
        str(record.get("mode", "?")),
    )


def _project_history_table_cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def _project_history_summary_row_key(row: str) -> tuple[str, str, str, str] | None:
    cells = _project_history_table_cells(row)
    if len(cells) < 4:
        return None
    return (cells[0], cells[1], cells[2], cells[3])


def _project_history_metric_row_key(row: str) -> tuple[str, str, str, str] | None:
    return _project_history_summary_row_key(row)


def _project_history_detail_block_key(block: str) -> tuple[str, str, str, str] | None:
    marker = "<summary>"
    start = block.find(marker)
    end = block.find("</summary>", start)
    if start == -1 or end == -1:
        return None
    summary = block[start + len(marker):end].strip()
    if " — " not in summary or " / " not in summary:
        return None
    date_time, rest = summary.split(" — ", 1)
    run_type, mode = rest.split(" / ", 1)
    return (date_time.strip(), "?", run_type.strip(), mode.strip())


def _project_history_keys_match(
    existing: tuple[str, str, str, str] | None,
    current: tuple[str, str, str, str],
) -> bool:
    if existing is None:
        return False
    same_session = (existing[0], existing[2], existing[3]) == (
        current[0],
        current[2],
        current[3],
    )
    return same_session and existing[1] in {current[1], "?"}


def _project_history_summary_row(record: dict) -> str:
    cells = [
        record.get("date_time", "?"),
        record.get("spec_path", "?"),
        record.get("run_type", "full"),
        record.get("mode", "?"),
        record.get("version", "?"),
        record.get("module_count", "0"),
        record.get("code_size", "0파일 / 0행"),
        record.get("total_duration", "0초"),
        record.get("md_summary", "0개 / 0행"),
        record.get("note", "-"),
    ]
    return "| " + " | ".join(_sanitize_history_cell(cell) for cell in cells) + " |"


def _project_history_metric_row(record: dict) -> str | None:
    metrics = record.get("quality_metrics")
    if metrics is None:
        return None

    quality_issues = record.get("quality_issues") or {}
    gate_status = quality_issues.get("status", "-")
    issue_count = len(quality_issues.get("issues", [])) if quality_issues else 0
    gate_detail = (
        f"{gate_status} ({issue_count} issues)" if quality_issues else "-"
    )
    cells = [
        record.get("date_time", "?"),
        record.get("spec_path", "?"),
        record.get("run_type", "full"),
        record.get("mode", "?"),
        (
            f"{metrics.evidence_precision:.2%} "
            f"({metrics.valid_source_tags}/{metrics.total_source_tags})"
        ),
        (
            f"{metrics.source_coverage:.2%} "
            f"({metrics.referenced_source_files}/{metrics.total_source_files})"
        ),
        (
            f"{metrics.core_coverage:.2%} "
            f"({metrics.referenced_core_modules}/{metrics.total_core_modules} 모듈)"
            if getattr(metrics, "core_coverage_unit", "file") == "module"
            else f"{metrics.core_coverage:.2%} "
            f"({metrics.referenced_core_files}/{metrics.total_core_files})"
        ),
        (
            f"{metrics.broken_source_link_rate:.2%} "
            f"({metrics.broken_source_links}/{metrics.total_source_links})"
        ),
        gate_detail,
    ]
    return "| " + " | ".join(_sanitize_history_cell(cell) for cell in cells) + " |"


def _project_history_detail_block(record: dict) -> str:
    summary = (
        f"{record.get('date_time', '?')} — "
        f"{record.get('run_type', 'full')} / {record.get('mode', '?')}"
    )
    lines = [
        "<details>",
        f"<summary>{_sanitize_history_cell(summary)}</summary>",
        "",
        "- Coding assistants: "
        + _sanitize_history_cell(", ".join(record.get("coding_agents") or []) or "-"),
        "",
        "| Workflow | Duration |",
        "|---|---:|",
    ]
    workflows = record.get("workflows") or []
    if workflows:
        for workflow, duration in workflows:
            lines.append(
                f"| {_sanitize_history_cell(workflow)} | {_sanitize_history_cell(duration)} |"
            )
    else:
        lines.append("| - | 0초 |")


    updated_specs = record.get("updated_specs") or []
    if updated_specs:
        lines.extend(
            [
                "",
                "### Updated Specs",
                "",
                "| Source | Overview | SDD | FR |",
                "|---|---|---|---|",
            ]
        )
        for spec in updated_specs:
            lines.append(
                _updated_spec_table_row(
                    spec,
                    base_dir=Path(record.get("project_root", ".")),
                    spec_root=Path(record.get("project_root", ".")),
                )
            )
    lines.extend(["", "</details>"])
    return "\n".join(lines)


def _normalize_project_history_content(
    content: str,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Normalize project history content into v2 hybrid summary/detail sections."""
    lines = content.splitlines()
    summary_rows = _extract_project_history_summary_rows(lines)
    metric_rows = _extract_project_history_metric_rows(lines)
    detail_blocks = _extract_project_history_detail_blocks(content)
    legacy_notes: list[str] = []

    if summary_rows or detail_blocks:
        return summary_rows, metric_rows, detail_blocks, legacy_notes

    records: list[dict] = []
    for line in lines:
        record = _project_history_record_from_legacy_row(line)
        if record is not None:
            records.append(record)
        elif _is_legacy_project_history_noise(line):
            continue
        elif line.strip():
            legacy_notes.append(line)

    return (
        [_project_history_summary_row(record) for record in records],
        [row for record in records if (row := _project_history_metric_row(record))],
        [_project_history_detail_block(record) for record in records],
        legacy_notes,
    )


def _extract_project_history_summary_rows(lines: list[str]) -> list[str]:
    in_summary = False
    rows: list[str] = []
    for line in lines:
        if line.strip() == PROJECT_HISTORY_SUMMARY_HEADING:
            in_summary = True
            continue
        if in_summary and line.startswith("## "):
            break
        if not in_summary:
            continue
        if (
            line.startswith("| ")
            and not line.startswith(PROJECT_HISTORY_HEADER)
            and not line.startswith("|---")
        ):
            rows.append(line)
    return rows


def _extract_project_history_metric_rows(lines: list[str]) -> list[str]:
    in_metrics = False
    rows: list[str] = []
    for line in lines:
        if line.strip() == PROJECT_HISTORY_METRICS_HEADING:
            in_metrics = True
            continue
        if in_metrics and line.startswith("## "):
            break
        if not in_metrics:
            continue
        if (
            line.startswith("| ")
            and not line.startswith(PROJECT_HISTORY_METRICS_HEADER)
            and not line.startswith("|---")
        ):
            rows.append(line)
    return rows


def _extract_project_history_detail_blocks(content: str) -> list[str]:
    blocks: list[str] = []
    start = 0
    while True:
        start = content.find("<details>", start)
        if start == -1:
            break
        end = content.find("</details>", start)
        if end == -1:
            break
        end += len("</details>")
        blocks.append(content[start:end].strip())
        start = end
    return blocks


def _render_project_history_content(
    summary_rows: list[str],
    metric_rows: list[str],
    detail_blocks: list[str],
    legacy_notes: list[str],
) -> str:
    lines = [
        "# Code2Spec Execution History",
        "",
        *PROJECT_HISTORY_NOTE.strip().splitlines(),
        "",
    ]

    if legacy_notes:
        lines.extend(["## Legacy Notes", "", *legacy_notes, ""])

    lines.extend(
        [
            PROJECT_HISTORY_SUMMARY_HEADING,
            "",
            PROJECT_HISTORY_HEADER,
            PROJECT_HISTORY_SEPARATOR,
            *summary_rows,
            "",
        ]
    )
    if metric_rows:
        lines.extend(
            [
                PROJECT_HISTORY_METRICS_HEADING,
                "",
                PROJECT_HISTORY_METRICS_HEADER,
                PROJECT_HISTORY_METRICS_SEPARATOR,
                *metric_rows,
                "",
            ]
        )
    lines.extend([PROJECT_HISTORY_DETAILS_HEADING, ""])
    for block in detail_blocks:
        lines.extend([block.strip(), ""])

    return "\n".join(lines).rstrip() + "\n"


def _normalize_project_history_table(content: str) -> str:
    """Backward-compatible wrapper for old table normalization callers."""
    summary_rows, metric_rows, detail_blocks, legacy_notes = (
        _normalize_project_history_content(content)
    )
    return _render_project_history_content(
        summary_rows, metric_rows, detail_blocks, legacy_notes
    )


def _project_history_record_from_legacy_row(line: str) -> dict | None:
    """Migrate legacy project-history rows to a v2 hybrid history record."""
    if not line.startswith("| ") or line.startswith("| **"):
        return None

    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if not cells or cells[0] in {"실행 날짜시간", "실행 일시"}:
        return None

    # Previous run-type aware format:
    # date/spec/version/run_type/mode/modules/code_size/workflows/total/md/note
    if len(cells) == 11:
        return {
            "date_time": _format_history_datetime(cells[0]),
            "spec_path": cells[1],
            "version": cells[2],
            "run_type": cells[3],
            "mode": cells[4],
            "module_count": cells[5],
            "code_size": cells[6],
            "workflows": _parse_workflow_summary(cells[7]),
            "total_duration": cells[8],
            "md_summary": cells[9],
            "note": cells[10],
        }

    # Legacy format without token:
    # date/spec/version/mode/modules/code_size/W1/W2/W3/total/md/note
    if len(cells) == 12:
        return {
            "date_time": _format_history_datetime(cells[0]),
            "spec_path": cells[1],
            "version": cells[2],
            "run_type": "full",
            "mode": cells[3],
            "module_count": cells[4],
            "code_size": cells[5],
            "workflows": [("W1", cells[6]), ("W2", cells[7]), ("W3", cells[8])],
            "total_duration": cells[9],
            "md_summary": cells[10],
            "note": cells[11],
        }

    # Legacy format with token:
    # date/spec/version/mode/modules/code_size/W1/W2/W3/total/token/md/note
    if len(cells) == 13:
        return {
            "date_time": _format_history_datetime(cells[0]),
            "spec_path": cells[1],
            "version": cells[2],
            "run_type": "full",
            "mode": cells[3],
            "module_count": cells[4],
            "code_size": cells[5],
            "workflows": [("W1", cells[6]), ("W2", cells[7]), ("W3", cells[8])],
            "total_duration": cells[9],
            "md_summary": cells[11],
            "note": cells[12],
        }

    return None


def _parse_workflow_summary(summary: str) -> list[tuple[str, str]]:
    if not summary or summary == "-":
        return []
    pairs: list[tuple[str, str]] = []
    for part in summary.split("/"):
        item = part.strip()
        if not item:
            continue
        name, _, duration = item.partition(" ")
        pairs.append((name, duration.strip() or "0초"))
    return pairs


def _is_legacy_project_history_noise(line: str) -> bool:
    stripped = line.strip()
    return (
        not stripped
        or stripped == "# Code2Spec Execution History"
        or stripped == PROJECT_HISTORY_SUMMARY_HEADING
        or stripped == PROJECT_HISTORY_DETAILS_HEADING
        or stripped.startswith("`코드 규모`")
        or stripped.startswith("> `코드 규모`")
        or stripped.startswith("> History format:")
        or stripped.startswith("| 실행 날짜시간 |")
        or stripped.startswith("| 실행 일시 |")
        or stripped.startswith("|--------------")
        or stripped.startswith("|---")
    )


def _migrate_project_history_row(line: str) -> str | None:
    """Migrate a legacy project-history row to a v2 summary row.

    Returns:
        - None: not a history data row.
        - str: normalized v2 summary row.
    """
    record = _project_history_record_from_legacy_row(line)
    if record is None:
        return None
    return _project_history_summary_row(record)


def _collect_markdown_stats(spec_root: Path) -> tuple[int, int]:
    """Collect count and total line count for user-facing Markdown artifacts."""
    md_files = [
        path
        for path in spec_root.glob("**/*.md")
        if ".analysis" not in path.parts and path.name != HISTORY_FILE
    ]
    total_lines = 0
    for md_file in md_files:
        try:
            total_lines += len(md_file.read_text(encoding="utf-8").splitlines())
        except OSError:
            continue
    return len(md_files), total_lines
