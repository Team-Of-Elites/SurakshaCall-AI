import asyncio
import io
import wave
from contextlib import suppress

from backend.app.audio.queues import AudioFrame, AudioQueueRegistry
from backend.app.config import Settings
from backend.app.schemas.transcript import TranscriptIn


class MobileAudioTranscriptionService:
    def __init__(self, settings: Settings, audio_queues: AudioQueueRegistry, sessions) -> None:
        self.settings = settings
        self.audio_queues = audio_queues
        self.sessions = sessions
        self._tasks: dict[str, asyncio.Task] = {}
        self._model = None
        self._model_error: str | None = None

    def ensure_session(self, session_id: str) -> None:
        if session_id not in self._tasks or self._tasks[session_id].done():
            self._tasks[session_id] = asyncio.create_task(self._run_session(session_id))

    async def stop_session(self, session_id: str) -> None:
        task = self._tasks.pop(session_id, None)
        if task and not task.done():
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        self.audio_queues.remove(session_id)

    async def shutdown(self) -> None:
        for session_id in list(self._tasks):
            await self.stop_session(session_id)

    async def _run_session(self, session_id: str) -> None:
        queue = self.audio_queues.get(session_id)
        buffer = bytearray()
        while True:
            frame = await queue.get()
            try:
                buffer.extend(frame.pcm)
                target_bytes = int(16_000 * 2 * self.settings.mobile_transcription_chunk_seconds)
                if len(buffer) >= target_bytes:
                    pcm = bytes(buffer)
                    buffer.clear()
                    text = await self.transcribe_pcm(pcm)
                    if text:
                        await self.sessions.submit_transcript(
                            session_id,
                            TranscriptIn(text=text, speaker="unknown", language="auto"),
                        )
            finally:
                queue.task_done()

    async def transcribe_pcm(self, pcm: bytes) -> str:
        if hasattr(self.settings, "test_transcript_override") and self.settings.test_transcript_override:
            return self.settings.test_transcript_override
        return await asyncio.to_thread(self._transcribe_sync, pcm)

    def _transcribe_sync(self, pcm: bytes) -> str:
        model = self._load_model()
        if model is None:
            return ""
        wav_bytes = _pcm_to_wav_bytes(pcm)
        segments, _info = model.transcribe(
            io.BytesIO(wav_bytes),
            language=None,
            vad_filter=True,
            beam_size=1,
        )
        return " ".join(segment.text.strip() for segment in segments).strip()

    def _load_model(self):
        if self._model is not None:
            return self._model
        if self._model_error:
            return None
        try:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                self.settings.whisper_model,
                device=getattr(self.settings, "whisper_device", "cpu"),
                compute_type=getattr(self.settings, "whisper_compute_type", "int8"),
            )
        except Exception as exc:
            self._model_error = str(exc)
            return None
        return self._model


def _pcm_to_wav_bytes(pcm: bytes) -> bytes:
    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16_000)
        wav_file.writeframes(pcm)
    return output.getvalue()
