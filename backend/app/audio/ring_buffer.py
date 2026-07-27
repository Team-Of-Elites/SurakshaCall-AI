"""
ring_buffer.py — Task O-04: In-Memory Circular PCM Ring Buffer

Provides a ~20-second circular byte buffer for raw PCM16 audio.
Prevents disk I/O, auto-evicts oldest samples, and supports retrieving pre-roll audio.
"""

import threading
from pydantic import BaseModel, computed_field


class AudioRingBuffer(BaseModel):
    def __init__(self, capacity_seconds: float = 20.0, sample_rate: int = 16000, sample_width: int = 2) -> None:
        super().__init__()
        self.sample_rate = sample_rate
        self.sample_width = sample_width
        self.bytes_per_second = sample_rate * sample_width
        self.max_bytes = int(capacity_seconds * self.bytes_per_second)
        self._buffer = bytearray()
        self._lock = threading.Lock()

    def append(self, pcm: bytes) -> None:
        with self._lock:
            self._buffer.extend(pcm)
            if len(self._buffer) > self.max_bytes:
                overflow = len(self._buffer) - self.max_bytes
                del self._buffer[:overflow]

    def get_pre_roll(self, duration_ms: int = 250) -> bytes:
        target_bytes = int((duration_ms / 1000.0) * self.bytes_per_second)
        with self._lock:
            if len(self._buffer) <= target_bytes:
                return bytes(self._buffer)
            return bytes(self._buffer[-target_bytes:])

    def get_all(self) -> bytes:
        with self._lock:
            return bytes(self._buffer)

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()

    @computed_field
    @property
    def current_bytes(self) -> int:
        with self._lock:
            return len(self._buffer)

    @computed_field
    @property
    def current_duration_seconds(self) -> float:
        with self._lock:
            return len(self._buffer) / float(self.bytes_per_second)
