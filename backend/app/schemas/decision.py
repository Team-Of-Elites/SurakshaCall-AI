# backend/app/schemas/decision.py
#Change made by Namit

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from .common import ProcessingMode, RiskLevel


class RiskComponents(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sensitive: int = Field(default=0, ge=0, le=30)
    manipulation: int = Field(default=0, ge=0, le=25)
    financial: int = Field(default=0, ge=0, le=15)
    identity: int = Field(default=0, ge=0, le=15)
    community: int = Field(default=0, ge=0, le=10)
    escalation: int = Field(default=0, ge=0, le=5)
    synergy: int = Field(default=0, ge=0, le=20)


class RiskBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    components: RiskComponents
    hard_score: float = Field(ge=0)
    soft_score: float = Field(ge=0)
    evidence_quality: float = Field(ge=0, le=1)
    uncertainty_penalty: float = Field(ge=0)
    raw_total: float = Field(ge=0)
    active_hard_floor: int = Field(ge=0, le=100)
    smoothed_score: float = Field(ge=0, le=100)
    final_score: int = Field(ge=0, le=100)
    top_evidence_ids: list[str] = Field(default_factory=list)
    policy_version: str = Field(min_length=1)


class RiskDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    state_version: int = Field(ge=0)
    risk_index: int = Field(ge=0, le=100)
    risk_level: RiskLevel

    headline: str
    reasons: list[str] = Field(default_factory=list)

    recommended_action_codes: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)

    uncertainty: str
    requires_immediate_warning: bool
    processing_mode: ProcessingMode
    degraded_modes: list[str] = Field(default_factory=list)

    risk_breakdown: RiskBreakdown
    generated_at_utc: datetime