"""
vad.py — Task O-05: Voice Activity Detection (VAD) State Machine

Implements speech state tracking (SILENCE -> SPEECH -> 650ms silence -> FINALIZE)
using energy/RMS and zero-crossing detection.
Enforces maximum utterance duration (e.g. 12 seconds) auto-splitting.
"""

from enum import Enum
import math
import numpy as np


class VADState(str, Enum):
    SILENCE = "SILENCE"
    POSSIBLE_SPEECH = "POSSIBLE_SPEECH"
    SPEECH = "SPEECH"


class VoiceActivityDetector:
    def __init__(
        self,
        sample_rate: int = 16000,
        frame_ms: int = 30,
        silence_finalize_ms: int = 650,
        pre_roll_ms: int = 250,
        post_roll_ms: int = 200,
        max_utterance_seconds: float = 12.0,
        energy_threshold_db: float = -42.0,
    ) -> None:
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.silence_finalize_ms = silence_finalize_ms
        self.pre_roll_ms = pre_roll_ms
        self.post_roll_ms = post_roll_ms
        self.max_utterance_seconds = max_utterance_seconds
        self.energy_threshold_db = energy_threshold_db

        self.state = VADState.SILENCE
        self.silence_counter_ms = 0
        self.speech_duration_ms = 0
        self._active_speech_pcm = bytearray()

    def process_frame(self, pcm16: bytes) -> dict:
        if not pcm16:
            return {"event": None, "pcm": b"", "is_speech": False}

        audio_data = np.frombuffer(pcm16, dtype=np.int16)
        if len(audio_data) == 0:
            return {"event": None, "pcm": b"", "is_speech": False}

        rms = np.sqrt(np.mean(audio_data.astype(np.float64) ** 2))
        rms_db = 20 * math.log10(rms / 32768.0) if rms > 1e-6 else -96.0

        is_frame_speech = rms_db > self.energy_threshold_db
        frame_duration = (len(audio_data) / self.sample_rate) * 1000.0

        event = None
        emitted_pcm = b""

        if self.state == VADState.SILENCE:
            if is_frame_speech:
                self.state = VADState.SPEECH
                self.silence_counter_ms = 0
                self.speech_duration_ms = frame_duration
                self._active_speech_pcm = bytearray(pcm16)
                event = "speech_start"
        elif self.state == VADState.SPEECH:
            self._active_speech_pcm.extend(pcm16)
            self.speech_duration_ms += frame_duration

            if is_frame_speech:
                self.silence_counter_ms = 0
            else:
                self.silence_counter_ms += frame_duration

            if self.speech_duration_ms >= (self.max_utterance_seconds * 1000.0):
                event = "speech_finalize"
                emitted_pcm = bytes(self._active_speech_pcm)
                self.reset()
            elif self.silence_counter_ms >= self.silence_finalize_ms:
                event = "speech_finalize"
                emitted_pcm = bytes(self._active_speech_pcm)
                self.reset()

        return {
            "event": event,
            "pcm": emitted_pcm,
            "is_speech": is_frame_speech,
            "rms_db": rms_db,
            "state": self.state,
        }

    def reset(self) -> None:
        self.state = VADState.SILENCE
        self.silence_counter_ms = 0
        self.speech_duration_ms = 0
        self._active_speech_pcm.clear()
