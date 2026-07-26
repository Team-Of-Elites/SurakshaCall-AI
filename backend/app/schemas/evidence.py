from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


Severity = Literal[1, 2, 3, 4, 5]


class EvidenceEvent(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid4()))
    utterance_id: str | None = None
    label: str
    description: str
    severity: Severity = 1
    confidence: float = 1.0
    source: str = "rules"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
