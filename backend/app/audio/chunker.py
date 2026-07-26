"""
chunker.py — Task O-05 / O-07: Audio Utterance Chunker

Assembles complete speech utterances by attaching pre-roll (250 ms)
and post-roll (200 ms) PCM audio around VAD-detected speech blocks.
"""

from backend.app.audio.ring_buffer import AudioRingBuffer


class AudioChunker:
    def __init__(
        self,
        ring_buffer: AudioRingBuffer,
        pre_roll_ms: int = 250,
        post_roll_ms: int = 200,
        sample_rate: int = 16000,
        sample_width: int = 2,
    ) -> None:
        self.ring_buffer = ring_buffer
        self.pre_roll_ms = pre_roll_ms
        self.post_roll_ms = post_roll_ms
        self.sample_rate = sample_rate
        self.sample_width = sample_width
        self.bytes_per_ms = (sample_rate * sample_width) / 1000.0

    def assemble_utterance(self, speech_pcm: bytes, include_pre_roll: bool = True) -> bytes:
        parts = []
        if include_pre_roll:
            pre_roll = self.ring_buffer.get_pre_roll(self.pre_roll_ms)
            parts.append(pre_roll)

        parts.append(speech_pcm)

        post_roll_bytes = int(self.post_roll_ms * self.bytes_per_ms)
        parts.append(b"\x00" * post_roll_bytes)

        return b"".join(parts)
