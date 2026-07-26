"""
microphone.py — Task O-03: Non-Blocking Microphone Capture Service

Captures 16 kHz 1-channel int16 PCM audio from the host microphone using sounddevice.
Pushes incoming audio frames to an asynchronous queue or callback.
Runs speech recognition safely off the callback thread.
"""

import asyncio
from typing import Callable
from backend.app.audio.devices import select_audio_device
from backend.app.audio.interfaces import AudioFrame


class MicrophoneCapture:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        frame_ms: int = 30,
        device_index: int | None = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.frame_ms = frame_ms
        self.device_index = device_index
        self.is_recording = False
        self._stream = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def start(
        self,
        session_id: str,
        on_frame_callback: Callable[[AudioFrame], None],
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> str:
        self.stop()
        self._loop = loop or asyncio.get_event_loop()
        resolved_index, device_name = select_audio_device(self.device_index)

        try:
            import sounddevice as sd

            block_size = int((self.sample_rate * self.frame_ms) / 1000)

            def audio_callback(indata, frames, time_info, status):
                if not self.is_recording:
                    return
                pcm_bytes = indata.tobytes()
                frame = AudioFrame(
                    session_id=session_id,
                    source="microphone",
                    track="mixed",
                    sample_rate=self.sample_rate,
                    channels=self.channels,
                    pcm16=pcm_bytes,
                )
                if self._loop and self._loop.is_running():
                    self._loop.call_soon_threadsafe(on_frame_callback, frame)

            self._stream = sd.InputStream(
                device=resolved_index,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype="int16",
                blocksize=block_size,
                callback=audio_callback,
            )
            self.is_recording = True
            self._stream.start()
            return f"Capture active on: {device_name}"
        except Exception as exc:
            self.is_recording = False
            return f"Microphone capture error (Fallback to replay mode): {str(exc)}"

    def stop(self) -> None:
        self.is_recording = False
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
