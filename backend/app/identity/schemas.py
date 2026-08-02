from typing import Literal

from pydantic import BaseModel, Field


class IdentityClaimCandidate(BaseModel):
    claim_id: str
    session_id: str = ""
    utterance_id: str = ""
    organization_text: str | None = None
    organization_type: str | None = None
    department: str | None = None
    evidence_quote: str = ""
    confidence: float = Field(ge=0, le=1, default=1.0)


class VerificationRequest(BaseModel):
    claim: IdentityClaimCandidate
    caller_number: str | None = None
    caller_number_source: Literal["phone_metadata", "manual_demo_input", "unknown"] = "unknown"
