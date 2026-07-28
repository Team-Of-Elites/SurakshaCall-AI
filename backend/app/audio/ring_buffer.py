"""
ring_buffer.py — Task O-04: In-Memory Circular PCM Ring Buffer

Provides a ~20-second circular byte buffer for raw PCM16 audio.
Prevents disk I/O, auto-evicts oldest samples, and supports retrieving pre-roll audio.
"""

import threading
from pydantic import BaseModel, PrivateAttr, computed_field


class AudioRingBuffer(BaseModel):
    capacity_seconds: float = 20.0
    sample_rate: int = 16000
    sample_width: int = 2

    _buffer: bytearray = PrivateAttr(default_factory=bytearray)
    _lock: threading.Lock = PrivateAttr(default_factory=threading.Lock)

    @property
    def bytes_per_second(self) -> int:
        return self.sample_rate * self.sample_width

    @property
    def max_bytes(self) -> int:
        return int(self.capacity_seconds * self.bytes_per_second)

    def append(self, pcm: bytes) -> None:
        with self._lock:
            self._buffer.extend(pcm)
            max_b = self.max_bytes
            if len(self._buffer) > max_b:
                overflow = len(self._buffer) - max_b
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

