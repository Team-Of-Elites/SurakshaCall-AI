from pydantic import BaseModel
from typing import Set, Optional

class CampaignFingerprint(BaseModel):
    schema_version: int = 1
    tactic_codes: Set[str]
    organization_type: Optional[str] = None
    scenario_code: Optional[str] = None
    requested_action_codes: Set[str]
    threat_codes: Set[str]
    payment_rail: Optional[str] = None
    channel_switch: Optional[str] = None
    language_family: Optional[str] = None
    country_code: str = "IN"