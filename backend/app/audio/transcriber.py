"""Mobile audio transcription service."""
import asyncio
import io
import wave
from contextlib import suppress

from backend.app.audio.queues import AudioQueueRegistry
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
        self._stats: dict[str, dict[str, object]] = {}

    def stats(self) -> dict[str, dict[str, object]]:
        return self._stats

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
        chunk_seconds = float(self.settings.mobile_transcription_chunk_seconds)
        target_bytes = int(16_000 * 2 * chunk_seconds)
        min_flush_bytes = min(target_bytes, 6_400)

        self._stats[session_id] = {
            "frames": 0, "bytes": 0, "chunks_finished": 0,
            "dropped": 0, "last_text": "", "last_error": "",
        }

        buffer = bytearray()
        while True:
            try:
                frame = await asyncio.wait_for(queue.get(), timeout=0.35)
            except asyncio.TimeoutError:
                if len(buffer) >= min_flush_bytes:
                    text = await self._transcribe(bytes(buffer), session_id)
                    if text:
                        s = self._stats.setdefault(session_id, {})
                        s["last_text"] = text
                        await self.sessions.submit_transcript(
                            session_id,
                            TranscriptIn(text=text, speaker="unknown", language="auto"),
                        )
                    buffer.clear()
                continue
            except asyncio.CancelledError:
                break

            try:
                s = self._stats.setdefault(session_id, {})
                s["frames"] = int(s.get("frames", 0)) + 1
                s["bytes"] = int(s.get("bytes", 0)) + len(frame.pcm)
                s["dropped"] = self.audio_queues.dropped().get(session_id, 0)

                buffer.extend(frame.pcm)
                if len(buffer) >= target_bytes:
                    pcm = bytes(buffer[:target_bytes])
                    import math, struct
                    samples_f32 = [struct.unpack('<h', pcm[i:i+2])[0] for i in range(0, min(8000, len(pcm)), 2)]
                    rms = math.sqrt(sum(s*s for s in samples_f32)/len(samples_f32)) if samples_f32 else 0
                    print(f"TRANSCRIBER: chunk {len(pcm)}bytes RMS={rms:.1f} session={session_id}", flush=True)
                    buffer = buffer[target_bytes:]
                    s["chunks_finished"] = int(s.get("chunks_finished", 0)) + 1
                    text = await self._transcribe(pcm, session_id)
                    if text:
                        s["last_text"] = text
                        await self.sessions.submit_transcript(
                            session_id,
                            TranscriptIn(text=text, speaker="unknown", language="auto"),
                        )
            except Exception as exc:
                print(f"TRANSCRIBER: error session={session_id} {exc}", flush=True)
            finally:
                queue.task_done()

    async def _transcribe(self, pcm: bytes, session_id: str | None, flush: bool = False) -> str:
        # Test override — returns fixed text without Whisper
        if hasattr(self.settings, "test_transcript_override") and self.settings.test_transcript_override:
            return self.settings.test_transcript_override

        # Real Whisper transcription
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self._transcribe_sync, pcm, session_id),
                timeout=15.0,
            )
        except asyncio.TimeoutError:
            print(f"TRANSCRIBER: timeout session={session_id}", flush=True)
            return ""
        except Exception as exc:
            print(f"TRANSCRIBER: error session={session_id} {exc}", flush=True)
            return ""

    def _transcribe_sync(self, pcm: bytes, session_id: str | None = None) -> str:
        import os
        if os.environ.get("TRANSCRIBE_MOCK") == "true":
            return "this is a mock transcription for testing"

        model = self._load_model()
        if model is None:
            return "[whisper not available]"
        wav_bytes = _pcm_to_wav_bytes(pcm)
        try:
            segments, info = model.transcribe(
                io.BytesIO(wav_bytes),
                language=None,
                vad_filter=True,
                beam_size=3,
                best_of=3,
                temperature=0.0,
                condition_on_previous_text=False,
            )
            text = " ".join(s.text.strip() for s in segments).strip()
            return text
        except Exception as exc:
            print(f"TRANSCRIBER: whisper fail session={session_id} {exc}", flush=True)
            return ""

    def _load_model(self):
        if self._model is not None:
            return self._model
        if self._model_error:
            return None
        try:
            from backend.app.stt.model_loader import WhisperModelLoader
            model, device, compute = WhisperModelLoader.get_model(
                model_size=self.settings.whisper_model,
                preferred_device=getattr(self.settings, "whisper_device", "cpu"),
                preferred_compute_type=getattr(self.settings, "whisper_compute_type", "int8"),
            )
            if model is not None:
                self._model = model
                print(f"TRANSCRIBER: Whisper loaded via WhisperModelLoader ({self.settings.whisper_model}, {device})", flush=True)
            else:
                self._model_error = "Whisper model load returned None"
        except Exception as exc:
            self._model_error = str(exc)
            print(f"TRANSCRIBER: load error: {exc}", flush=True)
        return self._model


def _pcm_to_wav_bytes(pcm: bytes) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16_000)
        w.writeframes(pcm)
    return buf.getvalue()
