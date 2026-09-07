#!/usr/bin/env python3
"""Local telemetry event stream and aggregate helpers for Code2Spec runs."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from ..analysis_paths import get_canonical_paths
    from ..git_context import extract_git_context
    from .common import (
        _load_runtime_stats,
        _save_runtime_stats,
    )
except ImportError:  # script/installed-tools flat execution
    from analysis_paths import get_canonical_paths
    from git_context import extract_git_context
    from progress.common import (
        _load_runtime_stats,
        _save_runtime_stats,
    )

TELEMETRY_EVENTS_FILE = "telemetry-events.jsonl"
TELEMETRY_CONFIG_FILE = "code2spec-config.json"
TELEMETRY_VERSION = "1.0"
WORKFLOW_NAMES = ("W1", "W2", "W3", "W-DELTA")
FAILURE_REASON_CATEGORIES = {
    "missing_prerequisite",
    "invalid_config",
    "command_failed",
    "quality_gate_failed",
    "source_parse_failed",
    "llm_generation_failed",
    "unknown",
}


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _normalize_workflow(workflow: str | None) -> str | None:
    if workflow is None:
        return None
    text = workflow.strip()
    return text.upper() if text else None


def _load_event_lines(output_dir: Path) -> list[dict[str, Any]]:
    path = get_canonical_paths(output_dir).telemetry_events
    if not path.exists():
        return []

    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events


def load_run_config(output_dir: Path) -> dict[str, Any]:
    """Load Code2Spec run config when present.

    The config is written beside runtime-stats.json and currently carries
    run-level analysis knobs such as analysis scope.
    """
    path = get_canonical_paths(output_dir).code2spec_config
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def _coerce_int(value: Any) -> int | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def resolve_run_context(
    stats: dict[str, Any] | None,
    config: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return normalized run-level fields for telemetry payloads."""
    stats = stats or {}
    config = config or {}
    analysis_scope = _coerce_int(
        stats.get("analysis_scope", config.get("analysis_scope"))
    )
    return {
        "analysis_scope": analysis_scope,
    }


def _candidate_git_paths(output_dir: Path, stats: dict[str, Any]) -> list[tuple[str, Path]]:
    candidates: list[tuple[str, Path]] = []
    for key in ("analysis_target", "workspace_root", "target_path"):
        value = stats.get(key)
        if isinstance(value, str) and value.strip():
            candidates.append((key, Path(value).expanduser()))
    candidates.append(("output_dir", output_dir))

    normalized: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for source, path in candidates:
        if not path.is_absolute():
            path = path.resolve()
        if path.is_file():
            path = path.parent
        key = str(path)
        if key not in seen and path.exists():
            seen.add(key)
            normalized.append((source, path))
    return normalized


def resolve_git_context(output_dir: Path, stats: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return minimal repository identity metadata when a git repo is found."""
    stats = stats or {}
    existing = stats.get("git")
    if isinstance(existing, dict) and existing.get("repo"):
        return existing

    for _detected_from, candidate in _candidate_git_paths(output_dir, stats):
        extracted = extract_git_context(candidate)
        if extracted["status"] not in {"ok", "incomplete"}:
            continue
        repo_root = Path(extracted["repo_root"])
        repository_id = extracted["repository"] or repo_root.name
        git_context: dict[str, Any] = {"repo": repository_id}
        if extracted["commit_id"]:
            git_context["commit"] = extracted["commit_id"]
        if extracted["branch"]:
            git_context["branch"] = extracted["branch"]
        if extracted["scm"] == "gerrit":
            gerrit_context: dict[str, Any] = {}
            if extracted["gerrit_project"]:
                gerrit_context["repo"] = extracted["gerrit_project"]
            if extracted["commit_id"]:
                gerrit_context["commit"] = extracted["commit_id"]
            if extracted["branch"]:
                gerrit_context["branch"] = extracted["branch"]
            if gerrit_context:
                git_context["gerrit"] = gerrit_context
        return git_context
    return None


def _event_base(output_dir: Path, event_type: str) -> dict[str, Any]:
    stats = _load_runtime_stats(output_dir)
    run_context = resolve_run_context(stats, load_run_config(output_dir))
    event = {
        "version": TELEMETRY_VERSION,
        "event_type": event_type,
        "timestamp": _now_iso(),
        "session_id": stats.get("session_id"),
        "run_type": stats.get("run_type"),
        "mode": stats.get("mode"),
        "analysis_target": stats.get("analysis_target") or stats.get("target_path"),
        **run_context,
    }
    coding_agent = stats.get("coding_agent")
    if isinstance(coding_agent, str) and coding_agent:
        event["coding_agent"] = coding_agent
    return event


def append_telemetry_event(
    output_dir: Path,
    event_type: str,
    *,
    workflow: str | None = None,
    payload: dict[str, Any] | None = None,
    update_aggregate: bool = True,
) -> dict[str, Any]:
    """Append a JSON Lines telemetry event and refresh the runtime aggregate."""
    output_dir.mkdir(parents=True, exist_ok=True)
    event = _event_base(output_dir, event_type)
    normalized_workflow = _normalize_workflow(workflow)
    if normalized_workflow:
        event["workflow"] = normalized_workflow
    if payload:
        event.update({key: value for key, value in payload.items() if value is not None})

    path = get_canonical_paths(output_dir).telemetry_events
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    if update_aggregate:
        update_runtime_telemetry(output_dir)
    return event


def _empty_workflow_usage() -> dict[str, Any]:
    return {
        "total_runs": 0,
        "by_workflow": {
            name: {
                "started": 0,
                "completed": 0,
                "in_progress": 0,
                "failed": 0,
                "attempt_count": 0,
                "completed_once": False,
            }
            for name in WORKFLOW_NAMES
        },
    }


def aggregate_telemetry(output_dir: Path) -> dict[str, Any]:
    """Build a compact telemetry aggregate from the local event stream."""
    events = _load_event_lines(output_dir)
    workflow_usage = _empty_workflow_usage()
    event_type_counts: dict[str, int] = {}
    regenerated_modules: set[str] = set()
    failed_modules: set[str] = set()
    module_usage = {
        "regenerated": 0,
        "failed": 0,
        "unique_regenerated": 0,
        "unique_failed": 0,
    }
    latest_event: dict[str, Any] | None = None
    latest_progress_event: dict[str, Any] | None = None
    latest_failure: dict[str, Any] | None = None
    coding_agents: set[str] = set()

    for event in events:
        event_type = event.get("event_type")
        if isinstance(event_type, str) and event_type:
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        if event_type == "module_regenerated":
            module_usage["regenerated"] += 1
            module = event.get("module")
            if isinstance(module, str) and module:
                regenerated_modules.add(module)
        elif event_type == "module_failed":
            module_usage["failed"] += 1
            module = event.get("module")
            if isinstance(module, str) and module:
                failed_modules.add(module)
        workflow = _normalize_workflow(event.get("workflow"))
        coding_agent = event.get("coding_agent")
        if isinstance(coding_agent, str) and coding_agent:
            coding_agents.add(coding_agent)
        compact_event = {
            key: event.get(key)
            for key in (
                "event_type",
                "timestamp",
                "workflow",
                "step",
                "module",
                "reason_category",
                "coding_agent",
            )
            if key in event
        }
        latest_event = compact_event
        if event_type not in {"workflow_failed", "module_failed"}:
            latest_progress_event = compact_event
        if workflow:
            bucket = workflow_usage["by_workflow"].setdefault(
                workflow,
                {
                    "started": 0,
                    "completed": 0,
                    "in_progress": 0,
                    "failed": 0,
                    "attempt_count": 0,
                    "completed_once": False,
                },
            )
            if event_type == "workflow_started":
                bucket["started"] += 1
                bucket["attempt_count"] += 1
                workflow_usage["total_runs"] += 1
            elif event_type == "workflow_completed":
                bucket["completed"] += 1
                bucket["completed_once"] = True
            elif event_type == "workflow_failed":
                bucket["failed"] += 1

        if event_type in {"workflow_failed", "module_failed"}:
            latest_failure = {
                key: event.get(key)
                for key in (
                    "event_type",
                    "timestamp",
                    "workflow",
                    "step",
                    "module",
                    "command",
                    "exit_code",
                    "reason_category",
                    "message",
                    "artifact_paths",
                    "retryable",
                    "coding_agent",
                )
                if key in event
            }

    module_usage["unique_regenerated"] = len(regenerated_modules)
    module_usage["unique_failed"] = len(failed_modules)

    for bucket in workflow_usage["by_workflow"].values():
        bucket["in_progress"] = max(
            int(bucket.get("started", 0))
            - int(bucket.get("completed", 0))
            - int(bucket.get("failed", 0)),
            0,
        )

    stats = _load_runtime_stats(output_dir)
    run_context = resolve_run_context(stats, load_run_config(output_dir))
    git_context = resolve_git_context(output_dir, stats)
    token_total = stats.get("total_token_usage")
    if isinstance(token_total, int) and token_total > 0:
        token_usage = {"status": "measured", "total": token_total}
    else:
        token_usage = {
            "status": "unknown",
            "total": token_total if isinstance(token_total, int) else None,
        }

    return {
        "version": TELEMETRY_VERSION,
        "events_file": TELEMETRY_EVENTS_FILE,
        "event_count": len(events),
        "event_type_counts": event_type_counts,
        **run_context,
        "git": git_context,
        "workflow_usage": workflow_usage,
        "module_usage": module_usage,
        "coding_agents": sorted(coding_agents),
        "latest_event": latest_event,
        "latest_progress_event": latest_progress_event,
        "latest_failure": latest_failure,
        "token_usage": token_usage,
        "updated_at": _now_iso(),
    }


def update_runtime_telemetry(output_dir: Path) -> dict[str, Any]:
    """Store the current telemetry aggregate under runtime-stats.json."""
    stats = _load_runtime_stats(output_dir)
    if not stats:
        return {}
    telemetry = aggregate_telemetry(output_dir)
    stats["telemetry"] = telemetry
    _save_runtime_stats(output_dir, stats)
    return telemetry


def _format_latest_event(event: dict[str, Any] | None) -> str:
    if not event:
        return "-"
    parts = [str(event.get("event_type", "-"))]
    if event.get("workflow"):
        parts.append(f"workflow={event['workflow']}")
    if event.get("module"):
        parts.append(f"module={event['module']}")
    if event.get("reason_category"):
        parts.append(f"reason={event['reason_category']}")
    if event.get("timestamp"):
        parts.append(f"at={event['timestamp']}")
    return " (" + ", ".join(parts[1:]) + ")" if len(parts) > 1 else parts[0]


def cmd_telemetry_summary(args: argparse.Namespace) -> None:
    """CLI entrypoint: print telemetry aggregate without requiring finalize-history."""
    output_dir = Path(args.output_dir)
    telemetry = aggregate_telemetry(output_dir)
    if getattr(args, "json", False):
        print(json.dumps(telemetry, ensure_ascii=False, indent=2, sort_keys=True))
        return

    events_path = get_canonical_paths(output_dir).telemetry_events
    print("[ProgressTracker] telemetry-summary")
    print(f"  Events: {telemetry.get('event_count', 0):,}")
    print(f"  Events file: {events_path}")
    git_context = telemetry.get("git")
    if isinstance(git_context, dict) and git_context.get("repo"):
        ref = git_context.get("branch") or str(git_context.get("commit", ""))[:12] or "unknown"
        print(f"  Git: {git_context.get('repo')} @ {ref}")

    coding_agents = telemetry.get("coding_agents", [])
    if isinstance(coding_agents, list) and coding_agents:
        print(f"  Coding assistants: {', '.join(map(str, coding_agents))}")

    token_usage = telemetry.get("token_usage", {})
    token_status = token_usage.get("status", "unknown") if isinstance(token_usage, dict) else "unknown"
    token_total = token_usage.get("total") if isinstance(token_usage, dict) else None
    if token_status == "measured" and isinstance(token_total, int):
        print(f"  Token usage: {token_total:,}")
    else:
        print("  Token usage: unknown")

    print("  Workflows:")
    workflow_usage = telemetry.get("workflow_usage", {})
    by_workflow = workflow_usage.get("by_workflow", {}) if isinstance(workflow_usage, dict) else {}
    printed_workflow = False
    for workflow, counts in by_workflow.items():
        if not isinstance(counts, dict):
            continue
        values = (
            counts.get("started", 0),
            counts.get("completed", 0),
            counts.get("in_progress", 0),
            counts.get("failed", 0),
            counts.get("attempt_count", 0),
        )
        if not any(values):
            continue
        printed_workflow = True
        print(
            "    "
            f"{workflow}: started={values[0]}, completed={values[1]}, "
            f"in_progress={values[2]}, failed={values[3]}, attempts={values[4]}"
        )
    if not printed_workflow:
        print("    -")

    module_usage = telemetry.get("module_usage", {})
    if isinstance(module_usage, dict):
        print(
            "  Modules: "
            f"regenerated={module_usage.get('regenerated', 0)}, "
            f"failed={module_usage.get('failed', 0)}, "
            f"unique_regenerated={module_usage.get('unique_regenerated', 0)}, "
            f"unique_failed={module_usage.get('unique_failed', 0)}"
        )

    event_type_counts = telemetry.get("event_type_counts", {})
    if isinstance(event_type_counts, dict) and event_type_counts:
        compact = ", ".join(
            f"{key}={value}" for key, value in sorted(event_type_counts.items())
        )
        print(f"  Event types: {compact}")

    print(f"  Latest event: {_format_latest_event(telemetry.get('latest_event'))}")
    latest_failure = telemetry.get("latest_failure")
    if isinstance(latest_failure, dict) and latest_failure:
        print(f"  Latest failure: {_format_latest_event(latest_failure)}")
    else:
        print("  Latest failure: -")


def cmd_telemetry_event(args: argparse.Namespace) -> None:
    """CLI entrypoint: append an arbitrary local telemetry event."""
    output_dir = Path(args.output_dir)
    payload: dict[str, Any] = {}
    for attr in (
        "step",
        "module",
        "command",
        "message",
        "reason_category",
        "retryable",
    ):
        value = getattr(args, attr, None)
        if value not in (None, ""):
            payload[attr] = value
    if getattr(args, "exit_code", None) is not None:
        payload["exit_code"] = args.exit_code
    if getattr(args, "artifact_path", None):
        payload["artifact_paths"] = args.artifact_path

    event = append_telemetry_event(
        output_dir,
        args.event,
        workflow=getattr(args, "workflow", None),
        payload=payload,
    )
    print(f"[ProgressTracker] telemetry-event: {event['event_type']}")
    print(f"  → {get_canonical_paths(output_dir).telemetry_events}")


def cmd_workflow_fail(args: argparse.Namespace) -> None:
    """CLI entrypoint: record a structured workflow failure event."""
    output_dir = Path(args.output_dir)
    workflow = _normalize_workflow(args.workflow)
    reason = args.reason_category or "unknown"
    if reason not in FAILURE_REASON_CATEGORIES:
        reason = "unknown"
    payload = {
        "step": args.step or "",
        "command": args.command_label or "",
        "exit_code": args.exit_code,
        "reason_category": reason,
        "message": args.message or "",
        "artifact_paths": args.artifact_path or [],
        "retryable": args.retryable,
    }
    event = append_telemetry_event(
        output_dir,
        "workflow_failed",
        workflow=workflow,
        payload=payload,
    )
    print(f"[ProgressTracker] {workflow} failed:")
    print(f"  Reason: {event.get('reason_category', 'unknown')}")
    print(f"  → {get_canonical_paths(output_dir).telemetry_events}")
