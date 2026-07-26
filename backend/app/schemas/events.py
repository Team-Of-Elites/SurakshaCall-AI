from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class EventType(StrEnum):
    SESSION_STARTED = "session_started"
    SESSION_SNAPSHOT = "session_snapshot"
    SESSION_RESET = "session_reset"
    AUDIO_STATUS = "audio_status"
    TRANSCRIPT_PARTIAL = "transcript_partial"
    TRANSCRIPT_FINAL = "transcript_final"
    FAST_DETECTION = "fast_detection"
    TACTIC_DETECTED = "tactic_detected"
    IDENTITY_CLAIMED = "identity_claimed"
    IDENTITY_VERIFIED = "identity_verified"
    COMMUNITY_MATCH = "community_match"
    RISK_UPDATE = "risk_update"
    SAFETY_WARNING = "safety_warning"
    PRIVACY_STATUS = "privacy_status"
    SYSTEM_STATUS = "system_status"
    SYSTEM_ERROR = "system_error"
    SESSION_ENDED = "session_ended"


class EventEnvelope(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    type: EventType
    session_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    sequence: int | None = None


def make_event(
    event_type: EventType,
    session_id: str,
    payload: dict[str, Any] | None = None,
) -> EventEnvelope:
    return EventEnvelope(type=event_type, session_id=session_id, payload=payload or {})
