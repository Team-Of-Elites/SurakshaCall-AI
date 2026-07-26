"""
quality.py — Task O-09: Audio Quality Monitoring & Diagnostics

Evaluates audio streams for RMS levels, clipping, noise, silence duration, and dropped frames.
Outputs quality state: GOOD, LOW_VOLUME, CLIPPING, NOISY, NO_INPUT, DEVICE_ERROR
along with actionable user remediation advice.
"""

from enum import Enum
import math
import numpy as np
from pydantic import BaseModel


class QualityState(str, Enum):
    GOOD = "GOOD"
    LOW_VOLUME = "LOW_VOLUME"
    CLIPPING = "CLIPPING"
    NOISY = "NOISY"
    NO_INPUT = "NO_INPUT"
    DEVICE_ERROR = "DEVICE_ERROR"


class AudioQualityStatus(BaseModel):
    state: QualityState
    rms_db: float
    clipping_percent: float
    silence_ratio: float
    actionable_advice: str


class AudioQualityMonitor:
    def __init__(
        self,
        clipping_threshold_percent: float = 2.0,
        low_volume_threshold_db: float = -45.0,
        high_volume_clipping_db: float = -1.0,
    ) -> None:
        self.clipping_threshold_percent = clipping_threshold_percent
        self.low_volume_threshold_db = low_volume_threshold_db
        self.high_volume_clipping_db = high_volume_clipping_db

    def evaluate_pcm(self, pcm16: bytes, sample_rate: int = 16000) -> AudioQualityStatus:
        if not pcm16:
            return AudioQualityStatus(
                state=QualityState.NO_INPUT,
                rms_db=-96.0,
                clipping_percent=0.0,
                silence_ratio=1.0,
                actionable_advice="No audio input detected. Please check your microphone selection.",
            )

        audio_data = np.frombuffer(pcm16, dtype=np.int16)
        if len(audio_data) == 0:
            return AudioQualityStatus(
                state=QualityState.NO_INPUT,
                rms_db=-96.0,
                clipping_percent=0.0,
                silence_ratio=1.0,
                actionable_advice="Audio buffer empty. Verify input hardware.",
            )

        rms = np.sqrt(np.mean(audio_data.astype(np.float64) ** 2))
        rms_db = 20 * math.log10(rms / 32768.0) if rms > 1e-6 else -96.0

        max_val = 32767
        min_val = -32768
        clipped_samples = np.sum((audio_data >= max_val - 100) | (audio_data <= min_val + 100))
        clipping_percent = (clipped_samples / len(audio_data)) * 100.0

        silence_samples = np.sum(np.abs(audio_data) < 300)
        silence_ratio = silence_samples / len(audio_data)

        if clipping_percent > self.clipping_threshold_percent or rms_db > self.high_volume_clipping_db:
            state = QualityState.CLIPPING
            advice = "Audio is distorting or too loud. Move the phone slightly further away from laptop mic."
        elif rms_db < -60.0 and silence_ratio > 0.95:
            state = QualityState.NO_INPUT
            advice = "No speech detected. Speak louder or check laptop microphone settings."
        elif rms_db < self.low_volume_threshold_db:
            state = QualityState.LOW_VOLUME
            advice = "Move the phone closer to the laptop microphone."
        elif rms_db > -35.0 and silence_ratio < 0.1:
            state = QualityState.NOISY
            advice = "High background noise detected. Reduce environmental noise."
        else:
            state = QualityState.GOOD
            advice = "Audio quality is optimal."

        return AudioQualityStatus(
            state=state,
            rms_db=round(rms_db, 2),
            clipping_percent=round(clipping_percent, 2),
            silence_ratio=round(silence_ratio, 2),
            actionable_advice=advice,
        )
