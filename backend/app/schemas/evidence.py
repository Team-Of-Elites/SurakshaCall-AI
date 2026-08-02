from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from .common import EvidenceSource, ScoreDimension


Severity = Literal[1, 2, 3, 4, 5]


class EvidenceEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    source: EvidenceSource
    label: str = Field(min_length=1)

    severity: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0, le=1)

    score_dimension: ScoreDimension
    score_delta: int
    risk_floor: int | None = Field(default=None, ge=0, le=100)

    utterance_ids: list[str] = Field(default_factory=list)
    evidence_quotes: list[str] = Field(default_factory=list)
    action_codes: list[str] = Field(default_factory=list)

    is_hard_evidence: bool = False
    persistent_for_session: bool = False

    created_ms: int = Field(ge=0)
    expires_ms: int | None = Field(default=None, ge=0)



# backend/app/schemas/evidence.py



