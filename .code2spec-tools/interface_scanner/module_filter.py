"""Filter interface candidates by module ownership for W2 integration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema import CandidateCollection, InterfaceCandidate, sort_candidates

DEFAULT_MODULE_CONTEXT_MAX_BYTES = 24_000
DEFAULT_EVIDENCE_LIMIT = 3
DEFAULT_PARTICIPANT_LIMIT = 4


def filter_candidates_for_module(
    collection: CandidateCollection,
    module_name: str,
    module_source_files: list[str],
) -> list[InterfaceCandidate]:
    """Filter candidates related to a specific module.

    A candidate is related to a module if any are true:
    - sender participant file is in module source files
    - receiver participant file is in module source files
    - constant participant file is in module source files
    - primary evidence file is in module source files
    - Android manifest component maps to a source file in module source files
    - logical module metadata includes the file path
    """
    # Normalize module source files for matching
    normalized_sources = set()
    for f in module_source_files:
        normalized_sources.add(f.replace("\\", "/"))
        # Also add without leading slash for relative matching
        if f.startswith("/"):
            normalized_sources.add(f.lstrip("/"))

    related: list[InterfaceCandidate] = []

    for candidate in collection.candidates:
        if _is_candidate_related(candidate, normalized_sources):
            related.append(candidate)

    return sort_candidates(related)


def _is_candidate_related(candidate: InterfaceCandidate, module_files: set[str]) -> bool:
    """Check if a candidate is related to a module by its source files."""
    # Check participants
    for _role_key, participants in candidate.participants.items():
        for p in participants:
            if _file_matches(p.file, module_files):
                return True

    # Check evidence files
    for ev in candidate.evidence:
        if _file_matches(ev.file, module_files):
            return True

    # Check module_refs (if already populated)
    for ref in candidate.module_refs:
        if _file_matches(ref.file, module_files):
            return True

    return False


def _file_matches(file_path: str, module_files: set[str]) -> bool:
    """Check if a file path matches any module source file."""
    normalized = file_path.replace("\\", "/")
    for mf in module_files:
        if normalized == mf or normalized.endswith("/" + mf) or mf.endswith("/" + normalized):
            return True
    return False


def write_module_candidate_context(
    output_dir: Path | str,
    module_name: str,
    module_source_files: list[str],
    candidates: list[InterfaceCandidate],
    *,
    max_context_bytes: int = DEFAULT_MODULE_CONTEXT_MAX_BYTES,
) -> Path:
    """Write compact per-module candidate context for W2 LLM review.

    ``interface-candidates.json`` remains the full machine-readable source of truth.
    This per-module artifact is intentionally compact and byte-budgeted so it is
    safe to paste/read in an LLM prompt. If the byte budget is exhausted, omitted
    IDs are written to a separate overflow artifact for traceability.

    Returns the compact context path.
    """
    output_dir = Path(output_dir)
    by_module_dir = output_dir / "interface-candidates" / "by-module"
    overflow_dir = output_dir / "interface-candidates" / "overflow"
    by_module_dir.mkdir(parents=True, exist_ok=True)

    safe_name = _safe_module_name(module_name)
    ranked = sort_candidates(candidates)
    budget = max(0, max_context_bytes)
    overflow_path = overflow_dir / f"{safe_name}.json"
    included_compact: list[dict[str, Any]] = []
    included_count = 0

    for candidate in ranked:
        trial_candidates = [*included_compact, _compact_candidate(candidate)]
        trial_context = _build_module_context(
            module_name=module_name,
            module_source_files=module_source_files,
            ranked=ranked,
            included_compact=trial_candidates,
            overflow_path=overflow_path,
            output_dir=output_dir,
            max_context_bytes=budget,
        )
        if _json_size_bytes(trial_context) > budget:
            break
        included_compact = trial_candidates
        included_count += 1

    omitted = ranked[included_count:]
    overflow_path_written: Path | None = None
    if omitted:
        overflow_dir.mkdir(parents=True, exist_ok=True)
        overflow_payload = {
            "module": module_name,
            "source_files": module_source_files,
            "omitted_reason": "max_context_bytes_exceeded",
            "max_context_bytes": budget,
            "omitted_count": len(omitted),
            "omitted_candidate_ids": [c.id for c in omitted],
            "full_source": "../../interface-candidates.json",
            "note": "Candidates are omitted in deterministic priority order after the compact context byte budget is exhausted.",
        }
        overflow_path.write_text(json.dumps(overflow_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        overflow_path_written = overflow_path

    context = _build_module_context(
        module_name=module_name,
        module_source_files=module_source_files,
        ranked=ranked,
        included_compact=included_compact,
        overflow_path=overflow_path_written,
        output_dir=output_dir,
        max_context_bytes=budget,
    )

    path = by_module_dir / f"{safe_name}.json"
    path.write_text(json.dumps(context, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _build_module_context(
    *,
    module_name: str,
    module_source_files: list[str],
    ranked: list[InterfaceCandidate],
    included_compact: list[dict[str, Any]],
    overflow_path: Path | None,
    output_dir: Path,
    max_context_bytes: int,
) -> dict[str, Any]:
    included_count = len(included_compact)
    omitted_count = max(0, len(ranked) - included_count)
    return {
        "context_kind": "module_interface_candidate_context",
        "compact": True,
        "module": module_name,
        "source_files": module_source_files,
        "limits": {
            "max_context_bytes": max_context_bytes,
            "max_evidence_per_candidate": DEFAULT_EVIDENCE_LIMIT,
            "max_participants_per_role": DEFAULT_PARTICIPANT_LIMIT,
        },
        "budget_policy": {
            "basis": "utf8_json_bytes",
            "packing": "deterministic_priority_prefix",
            "priority": "verification rank, normalized name, primary file, line, id",
        },
        "total_candidate_count": len(ranked),
        "included_candidate_count": included_count,
        "omitted_candidate_count": omitted_count,
        "truncated": omitted_count > 0,
        "candidate_ids": [c["id"] for c in included_compact],
        "overflow": {
            "path": str(overflow_path.relative_to(output_dir)) if overflow_path else "",
            "full_source": "interface-candidates.json",
            "note": "Omitted candidates are not lost; inspect overflow/full source only when needed.",
        },
        "llm_review_rules": [
            "Use this compact module-local context, not the full interface-candidates.json, as prompt input.",
            "Do not promote candidate/low/llm_suggested items to confirmed without source evidence.",
            "If truncated=true, summarize included high-priority candidates and mention omitted_count.",
            "For omitted candidates, request or inspect the overflow artifact only if module behavior depends on them.",
        ],
        "candidates": included_compact,
    }


def _json_size_bytes(payload: dict[str, Any]) -> int:
    return len((json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def _compact_candidate(candidate: InterfaceCandidate) -> dict[str, Any]:
    """Return an LLM-friendly candidate summary without large raw payloads."""
    return {
        "id": candidate.id,
        "family": candidate.family.value,
        "kind": candidate.kind,
        "platform": candidate.platform,
        "framework": candidate.framework,
        "mechanism": candidate.mechanism,
        "name": candidate.name,
        "normalized_name": candidate.normalized_name,
        "direction": candidate.direction,
        "verification": candidate.verification.value,
        "promotion": candidate.promotion.value,
        "needs_human_review": candidate.needs_human_review,
        "confidence": candidate.confidence.to_dict(),
        "unresolved": candidate.unresolved,
        "participants": {
            role: [
                {
                    "file": p.file,
                    "line": p.line,
                    "symbol": p.symbol,
                    "expression": _clip(p.expression),
                }
                for p in participants[:DEFAULT_PARTICIPANT_LIMIT]
            ]
            for role, participants in candidate.participants.items()
        },
        "evidence": [
            {
                "type": e.type.value,
                "label": e.label,
                "file": e.file,
                "line_start": e.line_start,
                "strength": e.strength.value,
                "expression": _clip(e.expression),
            }
            for e in candidate.evidence[:DEFAULT_EVIDENCE_LIMIT]
        ],
    }


def _clip(value: str, limit: int = 180) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1] + "…"


def _safe_module_name(module_name: str) -> str:
    return module_name.replace("/", "_").replace("\\", "_")


def write_llm_suggestion(
    output_dir: Path | str,
    module_name: str,
    suggestion: dict[str, Any],
) -> Path:
    """Write an LLM-suggested candidate to a review file.

    The suggestion must have origin=module_llm, verification=llm_suggested,
    promotion=needs_human_review, needs_human_review=true.
    """
    output_dir = Path(output_dir)
    suggestions_dir = output_dir / "interface-candidates" / "llm-suggestions"
    suggestions_dir.mkdir(parents=True, exist_ok=True)

    # Enforce LLM suggestion rules
    suggestion["origin"] = "module_llm"
    suggestion["verification"] = "llm_suggested"
    suggestion["promotion"] = "needs_human_review"
    suggestion["needs_human_review"] = True

    path = suggestions_dir / f"{_safe_module_name(module_name)}.json"

    # Append to existing or create new
    existing: list[dict] = []
    if path.exists():
        try:
            raw = path.read_text(encoding="utf-8")
            existing = json.loads(raw)
            if not isinstance(existing, list):
                # Corrupt: backup and start fresh
                backup = path.with_suffix(".json.bak")
                backup.write_text(raw, encoding="utf-8")
                existing = []
        except (json.JSONDecodeError, OSError):
            # Corrupt JSON: backup and start fresh
            try:
                raw = path.read_text(encoding="utf-8")
                backup = path.with_suffix(".json.bak")
                backup.write_text(raw, encoding="utf-8")
            except OSError:
                pass
            existing = []

    existing.append(suggestion)
    path.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
