"""Generate human-readable Markdown report for message/IPC candidates."""

from __future__ import annotations

from .schema import (
    CandidateCollection,
    InterfaceCandidate,
    Verification,
)


def generate_markdown_report(collection: CandidateCollection) -> str:
    """Generate message-contract-candidates.md content."""
    lines: list[str] = []
    lines.append("# Message / IPC Contract Candidates")
    lines.append("")
    lines.append(f"**Generated**: {collection.generated_at}")
    lines.append(f"**Analysis Target**: {collection.analysis_target}")
    lines.append(f"**Families**: {', '.join(collection.families)}")
    lines.append("")

    # Summary
    metrics = collection.metrics
    msg_metrics = metrics.get("message", {})
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Candidates | {metrics.get('total', 0)} |")
    for v_level in ("confirmed", "likely", "candidate", "llm_suggested", "low"):
        count = metrics.get("by_verification", {}).get(v_level, 0)
        lines.append(f"| {v_level} | {count} |")
    lines.append("")
    lines.append(f"**Message Candidates**: {msg_metrics.get('total', 0)} total / "
                 f"{msg_metrics.get('confirmed', 0)} confirmed / "
                 f"{msg_metrics.get('likely', 0)} likely / "
                 f"{msg_metrics.get('candidate', 0)} candidate")
    lines.append("")

    # Group by verification level
    confirmed_likely = [c for c in collection.candidates if c.verification in (Verification.CONFIRMED, Verification.LIKELY)]
    unresolved = [c for c in collection.candidates if c.verification == Verification.CANDIDATE]
    llm_suggested = [c for c in collection.candidates if c.verification == Verification.LLM_SUGGESTED]
    low = [c for c in collection.candidates if c.verification == Verification.LOW]

    # Confirmed / Likely
    if confirmed_likely:
        lines.append("## Confirmed / Likely Contracts")
        lines.append("")
        lines.append("| Direction | Contract | Mechanism | Framework | Status | Evidence |")
        lines.append("|-----------|----------|-----------|-----------|--------|----------|")
        for c in confirmed_likely:
            evidence_str = ", ".join(f"{e.file}:L{e.line_start}" for e in c.evidence[:3])
            lines.append(f"| {c.direction} | `{c.name}` | {c.mechanism} | {c.framework} | {c.verification.value} | {evidence_str} |")
        lines.append("")

    # Unresolved / Candidate
    if unresolved:
        lines.append("## Unresolved / Review-Only Candidates")
        lines.append("")
        lines.append("| Candidate | Kind | Reason | Missing Evidence | Evidence |")
        lines.append("|-----------|------|--------|------------------|----------|")
        for c in unresolved:
            evidence_str = ", ".join(f"{e.file}:L{e.line_start}" for e in c.evidence[:2])
            unresolved_str = "; ".join(c.unresolved) if c.unresolved else "incomplete boundary"
            lines.append(f"| `{c.name}` | {c.kind} | {unresolved_str} | {unresolved_str} | {evidence_str} |")
        lines.append("")

    # LLM-suggested
    if llm_suggested:
        lines.append("## LLM-Suggested Review Items")
        lines.append("")
        lines.append("> These items were suggested during module review and are not confirmed protocol facts.")
        lines.append("")
        lines.append("| Candidate | Observation | Required Evidence Before Promotion |")
        lines.append("|-----------|-------------|-----------------------------------|")
        for c in llm_suggested:
            lines.append(f"| `{c.name}` | {c.mechanism} | source evidence needed |")
        lines.append("")

    # Low confidence (informational)
    if low:
        lines.append("## Low-Confidence Candidates (Analysis Only)")
        lines.append("")
        lines.append("> These candidates have weak/generic evidence only and are not promoted to module documentation.")
        lines.append("")
        lines.append("| Candidate | Kind | Evidence | Unresolved |")
        lines.append("|-----------|------|----------|------------|")
        for c in low:
            evidence_str = ", ".join(f"{e.file}:L{e.line_start}" for e in c.evidence[:2])
            unresolved_str = "; ".join(c.unresolved) if c.unresolved else "-"
            lines.append(f"| `{c.name}` | {c.kind} | {evidence_str} | {unresolved_str} |")
        lines.append("")

    if not collection.candidates:
        lines.append("## No Candidates Found")
        lines.append("")
        lines.append("No evidence-backed interface/protocol candidates were found in the analyzed codebase.")
        lines.append("")

    return "\n".join(lines)


def render_module_card_section(candidates: list[InterfaceCandidate]) -> str:
    """Render the IPC / Message / Interface Contracts section for a Module Design Card.

    Follows the rendering rules from Step 3 spec.
    """
    lines: list[str] = []
    lines.append("## IPC / Message / Interface Contracts")
    lines.append("")

    if not candidates:
        lines.append("No evidence-backed IPC/message/interface candidates were found for this module.")
        lines.append("")
        return "\n".join(lines)

    confirmed_likely = [c for c in candidates if c.verification in (Verification.CONFIRMED, Verification.LIKELY)]
    unresolved = [c for c in candidates if c.verification == Verification.CANDIDATE]
    llm_suggested = [c for c in candidates if c.verification == Verification.LLM_SUGGESTED]
    # low confidence hidden by default

    if confirmed_likely:
        lines.append("### Confirmed / Likely Contracts")
        lines.append("")
        lines.append("| Direction | Contract | Mechanism | Peer / Counterpart | Status | Evidence |")
        lines.append("|-----------|----------|-----------|-------------------|--------|----------|")
        for c in confirmed_likely:
            evidence_str = ", ".join(f"{e.file}:L{e.line_start}" for e in c.evidence[:3])
            peer = _infer_peer(c)
            lines.append(f"| {c.direction} | `{c.name}` | {c.mechanism} | {peer} | {c.verification.value} | {evidence_str} |")
        lines.append("")

    if unresolved:
        lines.append("### Unresolved / Review-Only Candidates")
        lines.append("")
        lines.append("| Candidate | Reason | Missing Evidence | Evidence |")
        lines.append("|-----------|--------|------------------|----------|")
        for c in unresolved:
            evidence_str = ", ".join(f"{e.file}:L{e.line_start}" for e in c.evidence[:2])
            unresolved_str = "; ".join(c.unresolved) if c.unresolved else "incomplete boundary"
            lines.append(f"| `{c.name}` | {unresolved_str} | {unresolved_str} | {evidence_str} |")
        lines.append("")

    if llm_suggested:
        lines.append("### LLM-Suggested Review Items")
        lines.append("")
        lines.append("> These items were suggested during module review and are not confirmed protocol facts.")
        lines.append("")
        lines.append("| Candidate | Observation | Required Evidence Before Promotion |")
        lines.append("|-----------|-------------|-----------------------------------|")
        for c in llm_suggested:
            lines.append(f"| `{c.name}` | {c.mechanism} | source evidence needed |")
        lines.append("")

    if not confirmed_likely and not unresolved and not llm_suggested:
        lines.append("No evidence-backed IPC/message/interface candidates were found for this module.")
        lines.append("")

    return "\n".join(lines)


def _infer_peer(c: InterfaceCandidate) -> str:
    """Infer a peer/counterpart description from candidate metadata."""
    if c.framework == "electron":
        if "renderer" in c.direction:
            return "main process"
        if "main" in c.direction:
            return "renderer process"
    if c.framework == "socket_io":
        if "client" in c.direction:
            return "Socket.IO server"
        return "Socket.IO client"
    if c.framework == "android":
        if c.kind == "broadcast_action":
            return "Android BroadcastReceiver"
        if c.kind == "aidl_interface":
            return "AIDL client"
    if "sender" in c.participants and "receiver" in c.participants:
        return "paired endpoint"
    return "unknown"
