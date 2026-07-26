from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


Speaker = Literal["caller", "user", "unknown"]


class Utterance(BaseModel):
    utterance_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    text: str
    redacted_text: str | None = None
    speaker: Speaker = "unknown"
    language: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    confidence: float | None = None
    is_final: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TranscriptIn(BaseModel):
    text: str
    speaker: Speaker = "unknown"
    language: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    confidence: float | None = None
    redacted_text: str | None = None
