from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class RiskSnapshot(BaseModel):
    risk: int = Field(ge=0, le=100)
    level: RiskLevel
    reason: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RiskDecision(BaseModel):
    session_id: str
    risk: int = Field(ge=0, le=100)
    level: RiskLevel
    action: str
    explanation: str
    evidence_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
