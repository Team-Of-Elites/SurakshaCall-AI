from pydantic import BaseModel
from typing import List, Optional

class CommunityFingerprint(BaseModel):
    """
    Structured representation of a scam or legitimate behavioral pattern.
    This contains no PII, raw audio, or raw text—only structural metadata.
    """
    id: Optional[str] = None
    schema_version: int = 1
    tactics: List[str]
    organization_type: str
    scenario: str
    requested_action: str
    threat_type: str
    channel_switch: str
    language_family: str
    
    class Config:
        schema_extra = {
            "example": {
                "schema_version": 1,
                "tactics": ["AUTHORITY", "URGENCY", "ISOLATION"],
                "organization_type": "BANK",
                "scenario": "BANK_KYC",
                "requested_action": "SECRET_CODE",
                "threat_type": "ACCOUNT_FREEZE",
                "channel_switch": "NONE",
                "language_family": "HI_EN"
            }
        }