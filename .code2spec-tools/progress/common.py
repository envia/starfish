#!/usr/bin/env python3
"""Shared constants and helpers for Code2Spec progress-related tools.

This module now uses canonical .analysis paths via analysis_paths module.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

try:
    from ..analysis_paths import get_canonical_paths
    from ..version import get_code2spec_version
except ImportError:  # script/installed-tools flat execution
    try:
        from analysis_paths import get_canonical_paths
        from version import get_code2spec_version
    except ImportError:  # pragma: no cover
        def get_code2spec_version() -> str:
            return "0+unknown"
        def get_canonical_paths(analysis_dir: Path):
            from analysis_paths import AnalysisPaths
            return AnalysisPaths.from_analysis_dir(analysis_dir)

# File names (relative to canonical directories)
PROGRESS_FILE = "analysis-progress.json"  # state/delta/
RUNTIME_STATS_FILE = "runtime-stats.json"  # reports/runtime/
TRACEABILITY_FILE = "modules-traceability.md"  # state/delta/
CONTEXT_SUMMARY_FILE = "context-summary.md"  # state/delta/
HISTORY_FILE = "history.md"  # top-level code2spec/
CHUNK_SIZE = 10

CODE2SPEC_VERSION = get_code2spec_version()
PROJECT_HISTORY_FORMAT_VERSION = "v2 hybrid"
PROJECT_HISTORY_NOTE = (
    "> `코드 규모`는 AST 파싱된 소스 파일 기준입니다. "
    "(hidden dot 경로 제외, 실행 시점 min_lines 설정 반영)\n"
    f"> History format: {PROJECT_HISTORY_FORMAT_VERSION}\n\n"
)
PROJECT_HISTORY_HEADER = (
    "| 실행 일시 | Spec 경로 | 유형 | 모드 | 버전 | 모듈 | 코드 규모 | "
    "총 소요 | MD 산출물 | 비고 |"
)
PROJECT_HISTORY_SEPARATOR = (
    "|---|---|---|---|---|---:|---|---:|---|---|"
)
PROJECT_HISTORY_SUMMARY_HEADING = "## Summary"
PROJECT_HISTORY_DETAILS_HEADING = "## Workflow Details"


def _load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat(timespec="seconds")
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _resolve_spec_root(output_dir: Path) -> Path:
    """Resolve the user-facing code2spec root from an operational output directory."""
    if output_dir.name == ".analysis":
        return output_dir.parent
    if output_dir.name == "code2spec":
        return output_dir
    return output_dir.parent


def _get_progress_path(output_dir: Path) -> Path:
    """Get canonical path for analysis-progress.json."""
    paths = get_canonical_paths(output_dir)
    return paths.analysis_progress


def _get_runtime_stats_path(output_dir: Path) -> Path:
    """Get canonical path for runtime-stats.json."""
    paths = get_canonical_paths(output_dir)
    return paths.runtime_stats


def _get_traceability_path(output_dir: Path) -> Path:
    """Get canonical path for modules-traceability.md."""
    paths = get_canonical_paths(output_dir)
    return paths.state_delta_dir / TRACEABILITY_FILE


def _get_context_summary_path(output_dir: Path) -> Path:
    """Get canonical path for context-summary.md."""
    paths = get_canonical_paths(output_dir)
    return paths.state_delta_dir / CONTEXT_SUMMARY_FILE


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def _format_duration(seconds: int) -> str:
    """초를 'N 분 M 초' 형식으로 변환."""
    if seconds < 60:
        return f"{seconds}초"
    minutes = seconds // 60
    secs = seconds % 60
    if secs == 0:
        return f"{minutes}분"
    return f"{minutes}분 {secs}초"


def _load_runtime_stats(output_dir: Path) -> dict:
    return _load_json(_get_runtime_stats_path(output_dir))


def _save_runtime_stats(output_dir: Path, data: dict) -> None:
    _save_json(_get_runtime_stats_path(output_dir), data)
