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
    DECISION_UPDATE = "decision_update"
    RISK_UPDATE = "risk_update"
    SAFETY_WARNING = "safety_warning"
    PRIVACY_STATUS = "privacy_status"
    SYSTEM_STATUS = "system_status"
    SYSTEM_ERROR = "system_error"
    SESSION_ENDED = "session_ended"


#Change made by Namit
class EventEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    schema_version: int = Field(default=1, ge=1)
    session_id: str = Field(min_length=1)
    sequence: int = Field(ge=0)
    state_version_seen: int | None = Field(default=None, ge=0)

    occurred_monotonic_ns: int = Field(ge=0)
    occurred_at_utc: datetime

    producer: str = Field(min_length=1)
    correlation_id: str | None = None
    causation_id: str | None = None

    payload: dict[str, Any]


def make_event(
    event_type: EventType,
    session_id: str,
    payload: dict[str, Any] | None = None,
) -> EventEnvelope:
    return EventEnvelope(type=event_type, session_id=session_id, payload=payload or {})
