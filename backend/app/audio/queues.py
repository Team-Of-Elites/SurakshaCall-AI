"""Shared audio queues for mobile, replay, and microphone PCM."""
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class AudioFrame:
    session_id: str
    pcm: bytes
    sample_rate: int = 16_000
    channels: int = 1
    sample_width: int = 2
    source: str = "mobile"
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AudioQueueRegistry:
    def __init__(self, maxsize: int = 200) -> None:
        self.maxsize = maxsize
        self._queues: dict[str, asyncio.Queue[AudioFrame]] = {}
        self._dropped: dict[str, int] = {}

    def get(self, session_id: str) -> asyncio.Queue[AudioFrame]:
        if session_id not in self._queues:
            self._queues[session_id] = asyncio.Queue(maxsize=self.maxsize)
            self._dropped[session_id] = 0
        return self._queues[session_id]

    async def put_mobile_pcm(self, session_id: str, pcm: bytes) -> None:
        await self.put_pcm(session_id=session_id, pcm=pcm, source="mobile")

    async def put_pcm(self, session_id: str, pcm: bytes, source: str = "mobile") -> None:
        if not pcm:
            return
        frame = AudioFrame(session_id=session_id, pcm=pcm, source=source)
        q = self.get(session_id)
        try:
            q.put_nowait(frame)
        except asyncio.QueueFull:
            self._dropped[session_id] = self._dropped.get(session_id, 0) + 1

    async def put_audio_frame(self, frame) -> None:
        pcm = getattr(frame, "pcm", None) or getattr(frame, "pcm16", b"")
        source = getattr(frame, "source", "unknown")
        await self.put_pcm(session_id=frame.session_id, pcm=pcm, source=source)

    def remove(self, session_id: str) -> None:
        self._queues.pop(session_id, None)
        self._dropped.pop(session_id, None)

    def sizes(self) -> dict[str, int]:
        return {
            sid: q.qsize()
            for sid, q in self._queues.items()
        }

    def dropped(self) -> dict[str, int]:
        return dict(self._dropped)
