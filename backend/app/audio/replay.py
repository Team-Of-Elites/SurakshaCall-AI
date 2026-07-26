"""
replay.py — Task O-06: Timed Audio Replay Engine

Streams prerecorded WAV files in timed chunks (20-30 ms) at real-time 1.0x speed.
Feeds into the exact same VAD, Whisper, detection, and risk pipeline as live microphone audio.
"""

import asyncio
from typing import Callable, Coroutine
import wave
import numpy as np
from backend.app.audio.interfaces import AudioFrame


class TimedReplayEngine:
    def __init__(self, target_sample_rate: int = 16000) -> None:
        self.target_sample_rate = target_sample_rate
        self.is_running = False
        self._task: asyncio.Task | None = None

    def validate_and_load_wav(self, wav_path: str) -> tuple[bytes, int, int]:
        with wave.open(wav_path, "rb") as wf:
            n_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            raw_data = wf.readframes(n_frames)

        if sample_width == 2:
            audio_array = np.frombuffer(raw_data, dtype=np.int16)
        elif sample_width == 4:
            audio_array = (np.frombuffer(raw_data, dtype=np.int32) / 65536.0).astype(np.int16)
        else:
            audio_array = (np.frombuffer(raw_data, dtype=np.uint8).astype(np.int16) - 128) * 256

        if n_channels > 1:
            audio_array = audio_array.reshape(-1, n_channels).mean(axis=1).astype(np.int16)

        if framerate != self.target_sample_rate and len(audio_array) > 0:
            indices = np.round(np.arange(0, len(audio_array), framerate / float(self.target_sample_rate)))
            indices = indices[indices < len(audio_array)].astype(int)
            audio_array = audio_array[indices]

        return audio_array.tobytes(), self.target_sample_rate, 1

    async def start_replay(
        self,
        wav_path: str,
        session_id: str,
        on_frame: Callable[[AudioFrame], Coroutine[None, None, None]],
        frame_ms: int = 30,
        speed_factor: float = 1.0,
    ) -> None:
        self.stop()
        pcm16, sample_rate, channels = self.validate_and_load_wav(wav_path)

        bytes_per_ms = (sample_rate * channels * 2) / 1000.0
        chunk_bytes = int(frame_ms * bytes_per_ms)
        sleep_duration = (frame_ms / 1000.0) / max(0.1, speed_factor)

        self.is_running = True
        offset = 0

        while self.is_running and offset < len(pcm16):
            chunk = pcm16[offset : offset + chunk_bytes]
            offset += chunk_bytes
            if len(chunk) == 0:
                break

            frame = AudioFrame(
                session_id=session_id,
                source="replay",
                track="mixed",
                sample_rate=sample_rate,
                channels=channels,
                pcm16=chunk,
            )
            await on_frame(frame)
            await asyncio.sleep(sleep_duration)

        self.is_running = False

    def stop(self) -> None:
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
