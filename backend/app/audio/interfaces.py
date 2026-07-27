"""
interfaces.py — Task O-01: Common Audio Interfaces & Models

Defines the core data structures for audio frame transport across microphone capture,
replay engine, and mobile input sources.
"""

import time
from typing import Literal
from pydantic import BaseModel, Field, computed_field


class AudioFrame(BaseModel):
    session_id: str = "default_session"
    source: Literal["microphone", "replay", "mobile"] = "microphone"
    track: Literal["mixed", "unknown"] = "mixed"
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    sample_rate: int = 16000
    channels: int = 1
    sample_width: int = 2
    pcm16: bytes

    @computed_field
    @property
    def duration_ms(self) -> float:
        """Calculates frame duration in milliseconds."""
        bytes_per_sample = self.sample_width * self.channels
        if bytes_per_sample == 0 or self.sample_rate == 0:
            return 0.0
        num_samples = len(self.pcm16) / bytes_per_sample
        return (num_samples / self.sample_rate) * 1000.0
