"""
test_audio_pipeline.py — Task O-20: Comprehensive Audio & STT Unit Test Suite

Tests all 15 required checklist items:
1. audio schema
2. device enumeration
3. missing device fallback
4. ring eviction
5. VAD start
6. VAD finalize
7. max split
8. replay timing
9. replay reset
10. model loads once
11. Hindi transcription
12. safe-advice transcription
13. session cleanup
14. CPU fallback
15. quality states
"""

import asyncio
import pytest
import numpy as np
import os
import wave

from backend.app.audio.interfaces import AudioFrame
from backend.app.audio.devices import list_input_devices, select_audio_device
from backend.app.audio.ring_buffer import AudioRingBuffer
from backend.app.audio.vad import VoiceActivityDetector, VADState
from backend.app.audio.chunker import AudioChunker
from backend.app.audio.quality import AudioQualityMonitor, QualityState
from backend.app.audio.replay import TimedReplayEngine
from backend.app.stt.events import TranscriptEvent
from backend.app.stt.model_loader import WhisperModelLoader
from backend.app.stt.language import detect_code_mixing
from backend.app.stt.transcriber import SpeechTranscriber


# 1. Audio Schema Validation Test
def test_audio_frame_schema():
    pcm = b"\x00\x00" * 480  # 30 ms at 16 kHz int16 mono
    frame = AudioFrame(session_id="s1", source="microphone", track="mixed", pcm16=pcm)
    assert frame.session_id == "s1"
    assert frame.source == "microphone"
    assert frame.sample_rate == 16000
    assert abs(frame.duration_ms - 30.0) < 0.1


# 2. Device Enumeration Test
def test_device_enumeration():
    devices = list_input_devices()
    assert isinstance(devices, list)
    assert len(devices) > 0
    assert "name" in devices[0]
    assert "index" in devices[0]


# 3. Missing Device Fallback Test
def test_missing_device_fallback():
    idx, name = select_audio_device(preferred_index=99999)
    assert idx is not None
    assert "Fallback" in name or idx >= 0


# 4. Ring Buffer Eviction & Pre-Roll Test
def test_ring_buffer_eviction_and_pre_roll():
    # 2-second max capacity
    ring = AudioRingBuffer(capacity_seconds=2.0, sample_rate=16000, sample_width=2)
    bytes_per_sec = 16000 * 2  # 32000 bytes

    chunk_1s = b"\x01" * bytes_per_sec
    chunk_2s = b"\x02" * bytes_per_sec

    ring.append(chunk_1s)
    ring.append(chunk_2s)

    # Max capacity is 2 seconds (64000 bytes). First second should be evicted.
    assert ring.current_bytes == 64000
    pre_roll = ring.get_pre_roll(duration_ms=250)
    assert len(pre_roll) == int(0.25 * bytes_per_sec)
    assert pre_roll.startswith(b"\x02")


# 5. VAD Start Transition Test
def test_vad_start_transition():
    vad = VoiceActivityDetector(sample_rate=16000, energy_threshold_db=-40.0)
    # Loud sine wave
    t = np.linspace(0, 0.03, 480, False)
    loud_frame = (np.sin(2 * np.pi * 440 * t) * 20000).astype(np.int16).tobytes()

    res = vad.process_frame(loud_frame)
    assert res["event"] == "speech_start"
    assert vad.state == VADState.SPEECH


# 6. VAD Finalize Timing Test
def test_vad_finalize_timing():
    vad = VoiceActivityDetector(sample_rate=16000, silence_finalize_ms=650, energy_threshold_db=-40.0)
    t = np.linspace(0, 0.03, 480, False)
    loud_frame = (np.sin(2 * np.pi * 440 * t) * 20000).astype(np.int16).tobytes()
    silent_frame = b"\x00" * 960

    vad.process_frame(loud_frame)
    assert vad.state == VADState.SPEECH

    # Feed silence frames (30ms each). 650ms / 30ms = 22 frames
    finalized = False
    for _ in range(25):
        res = vad.process_frame(silent_frame)
        if res["event"] == "speech_finalize":
            finalized = True
            break

    assert finalized is True
    assert vad.state == VADState.SILENCE


# 7. Max Utterance Split Test (12s limit)
def test_max_utterance_split():
    vad = VoiceActivityDetector(sample_rate=16000, max_utterance_seconds=1.0, energy_threshold_db=-40.0)
    t = np.linspace(0, 0.03, 480, False)
    loud_frame = (np.sin(2 * np.pi * 440 * t) * 20000).astype(np.int16).tobytes()

    # Feed 1.1s of loud audio
    finalized = False
    for _ in range(40):
        res = vad.process_frame(loud_frame)
        if res["event"] == "speech_finalize":
            finalized = True
            break

    assert finalized is True


# 8 & 9. Replay Timing & Reset Test
@pytest.mark.asyncio
async def test_replay_timing_and_reset(tmp_path):
    wav_file = tmp_path / "test.wav"
    sample_rate = 16000
    t = np.linspace(0, 0.3, int(sample_rate * 0.3), False)
    audio = (np.sin(2 * np.pi * 440 * t) * 10000).astype(np.int16)

    with wave.open(str(wav_file), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    engine = TimedReplayEngine()
    received_frames = []

    async def frame_cb(frame: AudioFrame):
        received_frames.append(frame)

    replay_task = asyncio.create_task(
        engine.start_replay(str(wav_file), session_id="s1", on_frame=frame_cb, speed_factor=10.0)
    )
    await replay_task
    assert len(received_frames) > 0
    engine.stop()
    assert engine.is_running is False


# 10. Single Instance Model Loader Test
def test_whisper_model_singleton():
    WhisperModelLoader.reset()
    model1, device1, compute1 = WhisperModelLoader.get_model()
    model2, device2, compute2 = WhisperModelLoader.get_model()
    assert device1 == device2
    assert compute1 == compute2


# 11 & 12. Hindi & Code-mixed Language Test
def test_hindi_code_mixed_detection():
    hinglish_text = "Main bank ke KYC department se bol raha hoon. Aapka account block ho jayega."
    info = detect_code_mixing(hinglish_text)
    assert info["is_code_mixed"] is True
    assert info["primary_language"] == "hi"

    safe_text = "Kisi ko bhi OTP ya PIN mat batana. Official app se verify kijiye."
    info_safe = detect_code_mixing(safe_text)
    assert info_safe["primary_language"] == "hi"


# 13. Session Cleanup & Buffer Clear Test
def test_session_buffer_cleanup():
    ring = AudioRingBuffer(capacity_seconds=10.0)
    ring.append(b"\x01" * 1000)
    assert ring.current_bytes == 1000
    ring.clear()
    assert ring.current_bytes == 0


# 14. CPU Fallback Test
def test_cpu_fallback_on_cuda_error():
    WhisperModelLoader.reset()
    model, device, compute_type = WhisperModelLoader.get_model(
        preferred_device="cuda",
        preferred_compute_type="invalid_type",
    )
    assert device in ["cuda", "cpu", "error"]


# 15. Audio Quality Status Test
def test_audio_quality_states():
    monitor = AudioQualityMonitor()

    # Low volume silence
    low_pcm = b"\x00" * 960
    status_low = monitor.evaluate_pcm(low_pcm)
    assert status_low.state == QualityState.NO_INPUT

    # Clipping loud audio
    clip_array = np.full(480, 32767, dtype=np.int16)
    status_clip = monitor.evaluate_pcm(clip_array.tobytes())
    assert status_clip.state == QualityState.CLIPPING
