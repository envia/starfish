#!/usr/bin/env python3
"""Progress-state commands: init/status/next/update/context."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

try:
    from .telemetry import append_telemetry_event
except ImportError:  # script/installed-tools flat execution
    from progress.telemetry import append_telemetry_event

try:
    from .common import (
        CHUNK_SIZE,
        _dedupe_preserve_order,
        _get_context_summary_path,
        _get_progress_path,
        _get_traceability_path,
        _load_json,
        _load_runtime_stats,
        _save_json,
    )
except ImportError:  # script/installed-tools flat execution
    from progress.common import (
        CHUNK_SIZE,
        _dedupe_preserve_order,
        _get_context_summary_path,
        _get_progress_path,
        _get_traceability_path,
        _load_json,
        _load_runtime_stats,
        _save_json,
    )


def _load(output_dir: Path) -> dict:
    return _load_json(_get_progress_path(output_dir))


def _save(output_dir: Path, data: dict) -> None:
    _save_json(_get_progress_path(output_dir), data)


def _session_id_for_progress(output_dir: Path) -> str:
    """Reuse runtime-stats session id when present so progress/history stay aligned."""
    stats = _load_runtime_stats(output_dir)
    session_id = stats.get("session_id")
    if isinstance(session_id, str) and session_id:
        return session_id
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def cmd_init(args: argparse.Namespace) -> None:
    """모듈 목록 파일 또는 diff-plan.json을 읽어 진행 상태 초기화.

    --from-diff-plan 사용 시 changed/new/promoted/dependent/moved 모듈만 pending으로 들어가고,
    이미 처리된 unchanged 모듈은 completed로 분류된다 (skip 효과).
    """
    output_dir = Path(args.output_dir)
    diff_plan_path = getattr(args, "from_diff_plan", None)

    if diff_plan_path:
        modules, completed, mode = _modules_from_diff_plan(Path(diff_plan_path))
        if modules is None:
            return
        session_id = _session_id_for_progress(output_dir)
        data = {
            "session_id": session_id,
            "total_modules": len(modules) + len(completed),
            "chunk_size": CHUNK_SIZE,
            "completed": completed,
            "in_progress": None,
            "pending": modules,
            "failed": [],
            "delta": True,
            "diff_plan_path": str(Path(diff_plan_path).resolve()),
        }
        _save(output_dir, data)
        _init_traceability(output_dir, modules + completed, delta=True)
        print(
            f"[ProgressTracker] Initialized (delta): "
            f"{len(modules)} pending (regen targets), "
            f"{len(completed)} skipped (unchanged), "
            f"chunk_size={CHUNK_SIZE}"
        )
        print(f"  → {_get_progress_path(output_dir)}")
        if mode == "no_changes":
            print("  ℹ No regeneration targets. Module regeneration phase can skip.")
        return

    if not getattr(args, "modules_file", None):
        print("[ERROR] init requires either --modules-file or --from-diff-plan.")
        return
    modules_file = Path(args.modules_file)
    if not modules_file.exists():
        # Fallback: module-review가 생략되면
        # module-priority-reviewed.md가 없을 수 있음.
        # module-priority.md로 대체 시도
        fallback = modules_file.parent / "module-priority.md"
        if modules_file.name == "module-priority-reviewed.md" and fallback.exists():
            print(
                f"[ProgressTracker] ⚠ {modules_file.name} not found, "
                f"using module-priority.md as fallback"
            )
            modules_file = fallback
        else:
            print(f"[ERROR] modules-file not found: {modules_file}")
            return

    lines = modules_file.read_text(encoding="utf-8").splitlines()
    # | 모듈 | ... 형식 테이블에서 모듈명 추출 (헤더/구분선 제외)
    modules = []
    for line in lines:
        if (
            line.startswith("|")
            and not line.startswith("| 모듈")
            and not line.startswith("|---")
        ):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if parts:
                modules.append(parts[0])

    if not modules:
        # 줄 단위 목록 형식 시도
        modules = [
            line.strip().lstrip("-").strip()
            for line in lines
            if line.strip() and not line.startswith("#")
        ]

    session_id = _session_id_for_progress(output_dir)
    data = {
        "session_id": session_id,
        "total_modules": len(modules),
        "chunk_size": CHUNK_SIZE,
        "completed": [],
        "in_progress": None,
        "pending": modules,
        "failed": [],
    }
    _save(output_dir, data)
    _init_traceability(output_dir, modules)
    print(
        f"[ProgressTracker] Initialized: {len(modules)} modules, chunk_size={CHUNK_SIZE}"
    )
    print(f"  → {_get_progress_path(output_dir)}")


def _modules_from_diff_plan(
    diff_plan_path: Path,
) -> tuple[list[str] | None, list[str], str]:
    """diff-plan.json을 읽어 (pending, completed, mode_hint) 반환.

    pending = changed + new + promoted + dependent_changed + moved 모듈 file_path
    completed = unchanged 모듈 file_path (W2가 건너뛰도록)
    mode_hint = "no_changes" 또는 "ok"

    실패 시 (None, [], "") 반환.
    """
    if not diff_plan_path.exists():
        print(f"[ERROR] diff-plan not found: {diff_plan_path}")
        return None, [], ""
    try:
        data = json.loads(diff_plan_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[ERROR] Failed to read diff-plan: {exc}")
        return None, [], ""

    if data.get("invalidated"):
        reason = data.get("invalidated_reason", "")
        print(f"[ERROR] diff-plan is invalidated: {reason}")
        print("  → Run full W1+W2+W3 instead.")
        return None, [], ""

    changed = [item["file"] for item in data.get("changed_modules", [])]
    new = [item["file"] for item in data.get("new_modules", [])]
    promoted = [item["file"] for item in data.get("promoted_modules", [])]
    dependent_changed = [
        item["file"] for item in data.get("dependent_changed_modules", [])
    ]
    moved = [item["to"] for item in data.get("moved_modules", [])]
    unchanged = [item["file"] for item in data.get("unchanged_modules", [])]
    pending = _dedupe_preserve_order(
        changed + new + promoted + dependent_changed + moved
    )
    return pending, unchanged, "no_changes" if not pending else "ok"


def _init_traceability(
    output_dir: Path,
    modules: list[str],
    delta: bool = False,
) -> None:
    """traceability matrix 초기화.

    delta=True 일 때는 기존 traceability 를 보존하고 새 모듈에 대한
    행만 추가/upsert 한다. 미존재 모듈도 모두 보존 (=재실행 간 행 유지).
    """
    trace_path = _get_traceability_path(output_dir)

    if delta and trace_path.exists():
        existing = trace_path.read_text(encoding="utf-8").splitlines()
        existing_modules: set[str] = set()
        for line in existing:
            if (
                line.startswith("| ")
                and not line.startswith("| 모듈")
                and not line.startswith("|---")
            ):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 2 and parts[1]:
                    existing_modules.add(parts[1])
        # 새로 들어온 모듈 중 기존에 없던 것만 끝에 추가
        new_lines = list(existing)
        for m in modules:
            if m not in existing_modules:
                new_lines.append(f"| {m} | - | - | - | - | ⏳ 대기 |")
        trace_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return

    lines = [
        "# Modules Traceability Matrix",
        "",
        "| 모듈 | 파일 | FR 문서 | SDD 문서 | AST 분석 | 상태 |",
        "|------|------|---------|---------|---------|------|",
    ]
    for m in modules:
        lines.append(f"| {m} | - | - | - | - | ⏳ 대기 |")
    trace_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _remove_traceability_row(output_dir: Path, module: str) -> bool:
    """traceability 에서 특정 모듈 행 제거. 제거되면 True."""
    trace_path = _get_traceability_path(output_dir)
    if not trace_path.exists():
        return False
    lines = trace_path.read_text(encoding="utf-8").splitlines()
    new_lines: list[str] = []
    removed = False
    for line in lines:
        if line.startswith(f"| {module} |"):
            removed = True
            continue
        new_lines.append(line)
    if removed:
        trace_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return removed


def cmd_update(args: argparse.Namespace) -> None:
    """특정 모듈의 상태를 업데이트."""
    output_dir = Path(args.output_dir)
    data = _load(output_dir)
    if not data:
        print("[ERROR] No progress file found. Run 'init' first.")
        return

    module = args.module
    status = args.status  # done | failed | in_progress

    if status == "in_progress":
        data["in_progress"] = module
    elif status == "done":
        if module in data.get("pending", []):
            data["pending"].remove(module)
        if module not in data.get("completed", []):
            data["completed"].append(module)
        data["in_progress"] = None
        _update_traceability_row(output_dir, module, args)
        append_telemetry_event(
            output_dir,
            "module_regenerated",
            payload={"module": module, "status": "done"},
        )
    elif status == "failed":
        if module in data.get("pending", []):
            data["pending"].remove(module)
        if module not in data.get("failed", []):
            data["failed"].append(module)
        data["in_progress"] = None
        append_telemetry_event(
            output_dir,
            "module_failed",
            payload={
                "module": module,
                "reason_category": getattr(args, "reason_category", "unknown") or "unknown",
                "message": getattr(args, "message", "") or "",
                "retryable": True,
            },
        )

    data["completed_count"] = len(data.get("completed", []))
    _save(output_dir, data)
    print(f"[ProgressTracker] Updated: {module} → {status}")
    print(f"  Completed: {data['completed_count']}/{data['total_modules']}")


def _update_traceability_row(
    output_dir: Path, module: str, args: argparse.Namespace
) -> None:
    trace_path = _get_traceability_path(output_dir)
    if not trace_path.exists():
        return
    lines = trace_path.read_text(encoding="utf-8").splitlines()
    fr_doc = getattr(args, "fr_doc", "-") or "-"
    sdd_doc = getattr(args, "sdd_doc", "-") or "-"
    ast = getattr(args, "ast", "✅") or "✅"
    new_lines = []
    for line in lines:
        if line.startswith(f"| {module} |"):
            parts = [p.strip() for p in line.split("|")]
            # | 모듈 | 파일 | FR | SDD | AST | 상태 |
            if len(parts) >= 7:
                parts[3] = (
                    f"✅ [{Path(fr_doc).name}]({fr_doc})" if fr_doc != "-" else "-"
                )
                parts[4] = (
                    f"✅ [{Path(sdd_doc).name}]({sdd_doc})" if sdd_doc != "-" else "-"
                )
                parts[5] = ast
                parts[6] = "✅ 완료"
                new_lines.append(
                    "| " + " | ".join(p.strip() for p in parts[1:7]) + " |"
                )
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    trace_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def cmd_status(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    data = _load(output_dir)
    if not data:
        print("[ProgressTracker] No progress file found.")
        return
    total = data.get("total_modules", 0)
    completed = len(data.get("completed", []))
    pending = len(data.get("pending", []))
    failed = len(data.get("failed", []))
    in_prog = data.get("in_progress", "없음")
    pct = int(completed / total * 100) if total else 0
    print(f"[ProgressTracker] Session: {data.get('session_id', '?')}")
    print(f"  Progress: {completed}/{total} ({pct}%) | In progress: {in_prog}")
    print(f"  Pending: {pending} | Failed: {failed}")
    if failed:
        print(f"  Failed modules: {data['failed']}")


def cmd_next_chunk(args: argparse.Namespace) -> None:
    """다음 미완료 청크(최대 CHUNK_SIZE개) 출력."""
    output_dir = Path(args.output_dir)
    data = _load(output_dir)
    if not data:
        print("[ProgressTracker] No progress file found.")
        return
    pending = data.get("pending", [])
    if not pending:
        print("[ProgressTracker] ALL_DONE")
        return
    chunk = pending[:CHUNK_SIZE]
    print(f"[ProgressTracker] Next chunk ({len(chunk)}/{len(pending)} pending):")
    for m in chunk:
        print(f"  - {m}")


def cmd_append_context(args: argparse.Namespace) -> None:
    """청크 완료 후 핵심 정보를 context-summary.md 에 추가."""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = _get_context_summary_path(output_dir)
    data = _load(output_dir)
    total = data.get("total_modules", "?")
    completed = len(data.get("completed", []))
    chunk_num = completed // CHUNK_SIZE

    entry = [
        f"\n## Chunk {chunk_num} 완료 ({completed}/{total})",
        f"완료 모듈: {', '.join(data.get('completed', [])[-CHUNK_SIZE:])}",
    ]
    if args.pattern:
        entry.append(f"핵심 패턴: {args.pattern}")
    if args.dependencies:
        entry.append(f"주요 의존성: {args.dependencies}")

    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("\n".join(entry) + "\n")
    print(f"[ProgressTracker] Context appended → {summary_path}")
