"""Broad Interface Candidate Schema — data classes, enums, and validation.

Implements the schema defined in:
  .omx/specs/ipc-interface-protocol-step-1-schema.md
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ── Enumerations ──────────────────────────────────────────────────────────────


class Family(str, Enum):
    """Interface/protocol family."""

    MESSAGE = "message"
    HTTP_API = "http_api"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    DATABASE = "database"
    FILE_IO = "file_io"
    CLI = "cli"
    EXTERNAL_SERVICE = "external_service"
    CALLBACK_EVENT = "callback_event"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


class MessageKind(str, Enum):
    """Kind values for the ``message`` family."""

    IPC_CHANNEL = "ipc_channel"
    EVENT_NAME = "event_name"
    TOPIC = "topic"
    QUEUE = "queue"
    BROADCAST_ACTION = "broadcast_action"
    INTENT_ACTION = "intent_action"
    AIDL_INTERFACE = "aidl_interface"
    CONTENT_PROVIDER_URI = "content_provider_uri"
    WORKER_MESSAGE = "worker_message"
    POST_MESSAGE = "post_message"
    SOCKET_EVENT = "socket_event"
    MESSAGE_CONSTANT = "message_constant"
    UNKNOWN_MESSAGE = "unknown_message"


class Origin(str, Enum):
    """How the candidate was discovered."""

    SCANNER = "scanner"
    MODULE_LLM = "module_llm"
    HUMAN = "human"
    IMPORTED = "imported"


class Verification(str, Enum):
    """Verification / confidence level."""

    CONFIRMED = "confirmed"
    LIKELY = "likely"
    CANDIDATE = "candidate"
    LLM_SUGGESTED = "llm_suggested"
    LOW = "low"


class Promotion(str, Enum):
    """Where the candidate may appear in output."""

    SDD_ALLOWED = "sdd_allowed"
    MODULE_ALLOWED = "module_allowed"
    ANALYSIS_ONLY = "analysis_only"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


class EvidenceType(str, Enum):
    """Type of evidence backing a candidate."""

    KNOWN_IMPORT = "known_import"
    KNOWN_API = "known_api"
    GENERIC_API = "generic_api"
    CHANNEL_LITERAL = "channel_literal"
    CONSTANT_REFERENCE = "constant_reference"
    CONSTANT_DEFINITION = "constant_definition"
    SENDER_ENDPOINT = "sender_endpoint"
    RECEIVER_ENDPOINT = "receiver_endpoint"
    MANIFEST_DECLARATION = "manifest_declaration"
    CONFIG_DECLARATION = "config_declaration"
    LLM_OBSERVATION = "llm_observation"
    HUMAN_ANNOTATION = "human_annotation"


class ParticipantRole(str, Enum):
    """Role of a participant in a candidate."""

    SENDER = "sender"
    RECEIVER = "receiver"
    CONSTANT = "constant"
    PUBLISHER = "publisher"
    SUBSCRIBER = "subscriber"
    PROVIDER = "provider"
    CONSUMER = "consumer"
    OWNER = "owner"
    UNKNOWN = "unknown"


class ModuleRefRelationship(str, Enum):
    """How a module relates to a candidate."""

    SENDER_FILE = "sender_file"
    RECEIVER_FILE = "receiver_file"
    CONSTANT_FILE = "constant_file"
    MANIFEST_COMPONENT = "manifest_component"
    CONFIG_FILE = "config_file"
    LLM_RELATED = "llm_related"
    UNKNOWN_RELATED = "unknown_related"


class EvidenceStrength(str, Enum):
    """Strength of an evidence item."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Ordered by rank for deterministic sorting
VERIFICATION_RANK = {
    Verification.CONFIRMED: 0,
    Verification.LIKELY: 1,
    Verification.CANDIDATE: 2,
    Verification.LLM_SUGGESTED: 3,
    Verification.LOW: 4,
}


# ── Data classes ─────────────────────────────────────────────────────────────


@dataclass
class Evidence:
    """A single piece of evidence backing a candidate."""

    type: EvidenceType
    label: str
    file: str
    line_start: int
    line_end: int
    expression: str
    source: str  # e.g. "tree_sitter_call"
    strength: EvidenceStrength = EvidenceStrength.MEDIUM

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "label": self.label,
            "file": self.file,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "expression": self.expression,
            "source": self.source,
            "strength": self.strength.value,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Evidence:
        return cls(
            type=EvidenceType(d["type"]),
            label=d["label"],
            file=d["file"],
            line_start=d["line_start"],
            line_end=d["line_end"],
            expression=d["expression"],
            source=d["source"],
            strength=EvidenceStrength(d.get("strength", "medium")),
        )


@dataclass
class Participant:
    """A participant (sender/receiver/constant) in a candidate."""

    role: ParticipantRole
    file: str
    line: int
    symbol: str
    expression: str
    module: str = ""
    confidence: str = "candidate"  # verification-like for participant

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role.value,
            "file": self.file,
            "line": self.line,
            "symbol": self.symbol,
            "expression": self.expression,
            "module": self.module,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Participant:
        return cls(
            role=ParticipantRole(d["role"]),
            file=d["file"],
            line=d["line"],
            symbol=d["symbol"],
            expression=d["expression"],
            module=d.get("module", ""),
            confidence=d.get("confidence", "candidate"),
        )


@dataclass
class ModuleRef:
    """Reference from a candidate to a module."""

    module: str
    relationship: ModuleRefRelationship
    file: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "relationship": self.relationship.value,
            "file": self.file,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ModuleRef:
        return cls(
            module=d["module"],
            relationship=ModuleRefRelationship(d["relationship"]),
            file=d["file"],
        )


@dataclass
class Confidence:
    """Confidence assessment for a candidate."""

    label: str  # high / medium / low
    score: float
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "score": round(self.score, 4),
            "reasons": self.reasons,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Confidence:
        return cls(
            label=d["label"],
            score=d["score"],
            reasons=d.get("reasons", []),
        )


@dataclass
class InterfaceCandidate:
    """A single interface/protocol candidate.

    Implements the schema from Step 1 spec, section 4.
    """

    id: str
    family: Family
    kind: str  # Family-specific; e.g. MessageKind value for message family
    platform: str
    framework: str
    mechanism: str
    name: str
    normalized_name: str
    direction: str
    origin: Origin
    verification: Verification
    confidence: Confidence
    promotion: Promotion
    needs_human_review: bool
    participants: dict[str, list[Participant]] = field(default_factory=dict)
    evidence: list[Evidence] = field(default_factory=list)
    module_refs: list[ModuleRef] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        participants_out: dict[str, list[dict[str, Any]]] = {}
        for role_key, plist in self.participants.items():
            participants_out[role_key] = [p.to_dict() for p in plist]

        return {
            "id": self.id,
            "family": self.family.value,
            "kind": self.kind,
            "platform": self.platform,
            "framework": self.framework,
            "mechanism": self.mechanism,
            "name": self.name,
            "normalized_name": self.normalized_name,
            "direction": self.direction,
            "origin": self.origin.value,
            "verification": self.verification.value,
            "confidence": self.confidence.to_dict(),
            "promotion": self.promotion.value,
            "needs_human_review": self.needs_human_review,
            "participants": participants_out,
            "evidence": [e.to_dict() for e in self.evidence],
            "module_refs": [m.to_dict() for m in self.module_refs],
            "unresolved": self.unresolved,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> InterfaceCandidate:
        participants: dict[str, list[Participant]] = {}
        for role_key, plist in d.get("participants", {}).items():
            participants[role_key] = [Participant.from_dict(p) for p in plist]

        return cls(
            id=d["id"],
            family=Family(d["family"]),
            kind=d["kind"],
            platform=d.get("platform", ""),
            framework=d.get("framework", ""),
            mechanism=d.get("mechanism", ""),
            name=d.get("name", ""),
            normalized_name=d.get("normalized_name", ""),
            direction=d.get("direction", ""),
            origin=Origin(d["origin"]),
            verification=Verification(d["verification"]),
            confidence=Confidence.from_dict(d["confidence"]) if "confidence" in d else Confidence(label="low", score=0.0),
            promotion=Promotion(d["promotion"]),
            needs_human_review=d.get("needs_human_review", False),
            participants=participants,
            evidence=[Evidence.from_dict(e) for e in d.get("evidence", [])],
            module_refs=[ModuleRef.from_dict(m) for m in d.get("module_refs", [])],
            unresolved=d.get("unresolved", []),
            notes=d.get("notes", []),
        )


@dataclass
class CandidateCollection:
    """Top-level container for interface-candidates.json."""

    schema_version: int = 1
    generated_at: str = ""
    analysis_target: str = ""
    output_dir: str = ""
    generator_name: str = "interface-candidate-scanner"
    generator_version: str = "0.1.0"
    families: list[str] = field(default_factory=lambda: ["message"])
    candidates: list[InterfaceCandidate] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "analysis_target": self.analysis_target,
            "output_dir": self.output_dir,
            "generator": {
                "name": self.generator_name,
                "version": self.generator_version,
            },
            "families": self.families,
            "candidates": [c.to_dict() for c in self.candidates],
            "metrics": self.metrics,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CandidateCollection:
        gen = d.get("generator", {})
        return cls(
            schema_version=d.get("schema_version", 1),
            generated_at=d.get("generated_at", ""),
            analysis_target=d.get("analysis_target", ""),
            output_dir=d.get("output_dir", ""),
            generator_name=gen.get("name", "interface-candidate-scanner"),
            generator_version=gen.get("version", "0.1.0"),
            families=d.get("families", ["message"]),
            candidates=[InterfaceCandidate.from_dict(c) for c in d.get("candidates", [])],
            metrics=d.get("metrics", {}),
        )


# ── Deterministic ID generation ───────────────────────────────────────────────

def compute_candidate_id(
    family: str,
    kind: str,
    platform: str,
    framework: str,
    normalized_name: str,
    primary_file: str,
    primary_line: int,
    primary_expression: str,
) -> str:
    """Compute a deterministic candidate ID.

    Source key: ``family|kind|platform|framework|normalized_name|primary_file|primary_line|primary_expression_hash``
    Then hash using SHA-256 prefix → ``iface-msg-<12-char-hash>``.
    """
    expr_hash = hashlib.sha256(primary_expression.encode("utf-8")).hexdigest()[:8]
    source_key = "|".join([
        family,
        kind,
        platform,
        framework,
        normalized_name,
        primary_file,
        str(primary_line),
        expr_hash,
    ])
    h = hashlib.sha256(source_key.encode("utf-8")).hexdigest()[:12]
    return f"iface-msg-{h}"


# ── Deterministic sorting ─────────────────────────────────────────────────────

def sort_candidates(candidates: list[InterfaceCandidate]) -> list[InterfaceCandidate]:
    """Sort candidates deterministically.

    Order: family → verification rank → normalized_name → file path → line → id
    """
    def _sort_key(c: InterfaceCandidate) -> tuple:
        primary_file = ""
        primary_line = 0
        if c.evidence:
            primary_file = c.evidence[0].file
            primary_line = c.evidence[0].line_start
        return (
            c.family.value,
            VERIFICATION_RANK.get(c.verification, 99),
            c.normalized_name,
            primary_file,
            primary_line,
            c.id,
        )

    return sorted(candidates, key=_sort_key)


# ── Validation ───────────────────────────────────────────────────────────────

class ValidationError(Exception):
    """Raised when a candidate fails schema validation."""


def validate_candidate(c: InterfaceCandidate) -> list[str]:
    """Validate a single candidate against schema rules.

    Returns a list of error strings (empty if valid).
    """
    errors: list[str] = []

    # Required fields check
    if not c.id:
        errors.append("missing required field: id")
    if not c.family:
        errors.append("missing required field: family")
    if not c.kind:
        errors.append("missing required field: kind")
    if not c.origin:
        errors.append("missing required field: origin")
    if not c.verification:
        errors.append("missing required field: verification")
    if not c.promotion:
        errors.append("missing required field: promotion")

    # Enum validation
    try:
        Family(c.family.value)
    except ValueError:
        errors.append(f"invalid family: {c.family}")

    try:
        Origin(c.origin.value)
    except ValueError:
        errors.append(f"invalid origin: {c.origin}")

    try:
        Verification(c.verification.value)
    except ValueError:
        errors.append(f"invalid verification: {c.verification}")

    try:
        Promotion(c.promotion.value)
    except ValueError:
        errors.append(f"invalid promotion: {c.promotion}")

    # Promotion rule validation
    if c.verification == Verification.LOW and c.promotion == Promotion.SDD_ALLOWED:
        errors.append("verification=low cannot have promotion=sdd_allowed")

    if c.verification == Verification.LLM_SUGGESTED and c.promotion == Promotion.SDD_ALLOWED:
        errors.append("verification=llm_suggested cannot have promotion=sdd_allowed")

    # origin=module_llm implies verification=llm_suggested or needs_human_review=true
    if c.origin == Origin.MODULE_LLM:
        if c.verification != Verification.LLM_SUGGESTED and not c.needs_human_review:
            errors.append(
                "origin=module_llm requires verification=llm_suggested or needs_human_review=true"
            )

    # origin=module_llm with verification=confirmed is invalid unless human override
    if c.origin == Origin.MODULE_LLM and c.verification == Verification.CONFIRMED:
        errors.append(
            "origin=module_llm with verification=confirmed is invalid without human override"
        )

    # Evidence validation: source-backed evidence requires file/line/expression
    for i, ev in enumerate(c.evidence):
        if ev.source not in ("llm_observation", "human_annotation"):
            if not ev.file:
                errors.append(f"evidence[{i}]: source-backed evidence missing file")
            if ev.line_start <= 0:
                errors.append(f"evidence[{i}]: source-backed evidence missing line_start")
            if not ev.expression:
                errors.append(f"evidence[{i}]: source-backed evidence missing expression")

    return errors


def validate_collection(collection: CandidateCollection) -> list[str]:
    """Validate an entire CandidateCollection.

    Returns a list of error strings (empty if valid).
    """
    errors: list[str] = []

    # Top-level required fields
    if collection.schema_version != 1:
        errors.append(f"unsupported schema_version: {collection.schema_version}")

    # Validate each candidate
    for i, c in enumerate(collection.candidates):
        candidate_errors = validate_candidate(c)
        for err in candidate_errors:
            errors.append(f"candidate[{i}] ({c.id}): {err}")

    return errors
