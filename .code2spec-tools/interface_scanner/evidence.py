"""Intermediate evidence records for interface candidate scanning.

The scanner intentionally separates source evidence from final candidates:

source lines/imports/manifests -> EndpointRecord/ConstantRecord -> pairing -> InterfaceCandidate
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .schema import Confidence, Evidence, ParticipantRole, Promotion, Verification


@dataclass
class EndpointRecord:
    """A protocol endpoint observed in source before candidate pairing."""

    role: ParticipantRole
    family: str
    kind: str
    platform: str
    framework: str
    mechanism: str
    name: str
    normalized_name: str
    direction: str
    file: str
    line: int
    symbol: str
    expression: str
    evidence: list[Evidence] = field(default_factory=list)
    verification_hint: Verification = Verification.CANDIDATE
    promotion_hint: Promotion = Promotion.ANALYSIS_ONLY
    confidence: Confidence = field(default_factory=lambda: Confidence(label="low", score=0.0))
    unresolved: list[str] = field(default_factory=list)

    @property
    def pair_key(self) -> tuple[str, str, str, str, str]:
        """Stable key used for sender/receiver pairing."""
        return (
            self.family,
            self.kind,
            self.platform,
            self.framework,
            self.normalized_name,
        )


@dataclass
class ConstantRecord:
    """A message/interface-like constant before candidate construction."""

    family: str
    kind: str
    platform: str
    framework: str
    mechanism: str
    name: str
    normalized_name: str
    file: str
    line: int
    symbol: str
    expression: str
    evidence: list[Evidence] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
