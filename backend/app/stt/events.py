"""
events.py — Task O-07: Transcript Event Schemas

Defines the standard JSON transcript event schema emitted by speech-to-text.
Guarantees downstream compatibility with scam safety rules and multi-agent risk scoring.
"""

from typing import Literal
from uuid import uuid4
from pydantic import BaseModel, Field


class TranscriptEvent(BaseModel):
    utterance_id: str = Field(default_factory=lambda: f"utt_{str(uuid4())[:8]}")
    session_id: str
    track: Literal["mixed", "unknown"] = "mixed"
    speaker: Literal["caller", "user", "unknown"] = "unknown"
    text: str
    language: str = "en"
    started_ms: int
    ended_ms: int
    asr_confidence: float = 0.85
    input_mode: Literal["microphone", "replay", "mobile"] = "microphone"
