from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

VerificationStatus = Literal[
    "VERIFIED", "UNVERIFIED", "CONTRADICTORY", "INSUFFICIENT_DATA"
]


class IdentityClaim(BaseModel):
    claim_id: str = Field(default_factory=lambda: str(uuid4()))
    organization: str | None = None
    person_name: str | None = None
    role: str | None = None
    utterance_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VerificationResult(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid4()))
    claim_id: str | None = None
    status: VerificationStatus = "INSUFFICIENT_DATA"
    reason: str = "No trusted-directory result available."
    risk_contribution: int = 0
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CommunityMatch(BaseModel):
    match_id: str = Field(default_factory=lambda: str(uuid4()))
    status: VerificationStatus = "INSUFFICIENT_DATA"
    similarity: float = 0.0
    pattern_name: str | None = None
    reason: str = "Community intelligence unavailable in local skeleton."
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
