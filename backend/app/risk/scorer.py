from dataclasses import dataclass
from typing import Literal

RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

SEVERITY_WEIGHT = 8


@dataclass
class RiskUpdate:
    risk: int
    level: RiskLevel
    delta: int
    reason: str


def compute_risk_from_evidence(current_risk: int, evidence_severities: list[int]) -> RiskUpdate:
    if not evidence_severities:
        return RiskUpdate(risk=current_risk, level=_level_for_risk(current_risk), delta=0, reason="No new evidence.")
    added = sum(sev * SEVERITY_WEIGHT for sev in evidence_severities)
    new_risk = min(100, max(current_risk, current_risk + added))
    return RiskUpdate(
        risk=new_risk,
        level=_level_for_risk(new_risk),
        delta=added,
        reason=f"Added {added} risk from {len(evidence_severities)} evidence items.",
    )


def merge_identity_risk(current_risk: int, identity_contribution: int) -> RiskUpdate:
    if identity_contribution <= 0:
        return RiskUpdate(risk=current_risk, level=_level_for_risk(current_risk), delta=0, reason="No identity risk.")
    new_risk = min(100, current_risk + identity_contribution)
    return RiskUpdate(
        risk=new_risk,
        level=_level_for_risk(new_risk),
        delta=identity_contribution,
        reason=f"Identity check contributed {identity_contribution} risk.",
    )


def merge_community_risk(current_risk: int, similarity: float) -> RiskUpdate:
    contribution = int(similarity * 20)
    if contribution <= 0:
        return RiskUpdate(risk=current_risk, level=_level_for_risk(current_risk), delta=0, reason="No community match.")
    new_risk = min(100, current_risk + contribution)
    return RiskUpdate(
        risk=new_risk,
        level=_level_for_risk(new_risk),
        delta=contribution,
        reason=f"Community pattern matched with similarity {similarity:.2f}.",
    )


def _level_for_risk(risk: int) -> RiskLevel:
    if risk >= 85:
        return "CRITICAL"
    if risk >= 70:
        return "HIGH"
    if risk >= 40:
        return "MEDIUM"
    return "LOW"
