"""
transcriber.py — Task O-07 & O-08: High-Level Speech Transcriber Service

Converts PCM audio chunks into structured TranscriptEvent objects using faster-whisper.
Integrates language identification, timestamp tracking, and CUDA/CPU fallback options.
"""

import asyncio
import io
import time
import wave
from backend.app.stt.events import TranscriptEvent
from backend.app.stt.language import detect_code_mixing
from backend.app.stt.model_loader import WhisperModelLoader


class SpeechTranscriber:
    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        test_override_text: str | None = None,
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.test_override_text = test_override_text

    async def transcribe_pcm_chunk(
        self,
        pcm16: bytes,
        session_id: str,
        started_ms: int,
        ended_ms: int,
        input_mode: str = "microphone",
        sample_rate: int = 16000,
    ) -> TranscriptEvent | None:
        if self.test_override_text:
            return TranscriptEvent(
                session_id=session_id,
                text=self.test_override_text,
                language="en",
                started_ms=started_ms,
                ended_ms=ended_ms,
                asr_confidence=0.99,
                input_mode=input_mode,
            )

        if not pcm16:
            return None

        text, detected_lang, confidence = await asyncio.to_thread(
            self._transcribe_sync, pcm16, sample_rate
        )

        if not text or not text.strip():
            return None

        lang_info = detect_code_mixing(text)
        final_lang = lang_info["primary_language"] or detected_lang

        return TranscriptEvent(
            session_id=session_id,
            track="mixed",
            speaker="unknown",
            text=text.strip(),
            language=final_lang,
            started_ms=started_ms,
            ended_ms=ended_ms,
            asr_confidence=round(confidence, 2),
            input_mode=input_mode,
        )

    def _transcribe_sync(self, pcm16: bytes, sample_rate: int = 16000) -> tuple[str, str, float]:
        model, _device, _compute = WhisperModelLoader.get_model(
            model_size=self.model_size,
            preferred_device=self.device,
            preferred_compute_type=self.compute_type,
        )

        if model is None:
            return "", "en", 0.0

        wav_bytes = pcm_to_wav_bytes(pcm16, sample_rate)

        def run_transcribe(m, vad_flt: bool):
            segments, info = m.transcribe(
                io.BytesIO(wav_bytes),
                language=None,
                vad_filter=vad_flt,
                beam_size=1,
            )
            full_text = " ".join(segment.text.strip() for segment in segments).strip()
            confidence = getattr(info, "language_probability", 0.85)
            lang = getattr(info, "language", "en")
            return full_text, lang, confidence

        try:
            text, lang, conf = run_transcribe(model, False)
            if text:
                return text, lang, conf
        except Exception:
            pass

        # Fallback to CPU model if CUDA runtime failed
        cpu_model, _, _ = WhisperModelLoader.get_cpu_model(self.model_size)
        if cpu_model is not None:
            try:
                text, lang, conf = run_transcribe(cpu_model, False)
                return text, lang, conf
            except Exception:
                return "", "en", 0.0
        return "", "en", 0.0


def pcm_to_wav_bytes(pcm16: bytes, sample_rate: int = 16000) -> bytes:
    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm16)
    return output.getvalue()
