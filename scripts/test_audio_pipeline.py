"""
scripts/test_audio_pipeline.py — Task O-06/O-07 Integration Test Tool

Tests the full audio pipeline: AudioFrame -> VAD -> Whisper Transcriber -> TranscriptEvent & Quality Monitor.
Usage:
    python scripts/test_audio_pipeline.py
"""

import asyncio
import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.audio.interfaces import AudioFrame
from backend.app.audio.ring_buffer import AudioRingBuffer
from backend.app.audio.vad import VoiceActivityDetector
from backend.app.audio.chunker import AudioChunker
from backend.app.audio.quality import AudioQualityMonitor
from backend.app.stt.transcriber import SpeechTranscriber


async def main():
    print("==================================================")
    print("  SurakshaCall AI — Audio Pipeline Integration Test")
    print("==================================================")

    sample_rate = 16000
    ring_buf = AudioRingBuffer(capacity_seconds=20.0, sample_rate=sample_rate)
    vad = VoiceActivityDetector(sample_rate=sample_rate, energy_threshold_db=-40.0)
    chunker = AudioChunker(ring_buf)
    quality_monitor = AudioQualityMonitor()
    transcriber = SpeechTranscriber(test_override_text="Aapka account block ho jayega, urgent PIN enter kijiye.")

    duration_s = 1.5
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), False)
    speech_pcm = (np.sin(2 * np.pi * 300 * t) * 20000).astype(np.int16).tobytes()

    print("Simulating audio frame stream...")
    frame_ms = 30
    bytes_per_frame = int((sample_rate * 2 * frame_ms) / 1000)
    offset = 0

    session_id = "test_session_001"
    start_time = int(time.time() * 1000)

    speech_chunks = []

    while offset < len(speech_pcm):
        pcm_frame = speech_pcm[offset : offset + bytes_per_frame]
        offset += bytes_per_frame
        if not pcm_frame:
            break

        ring_buf.append(pcm_frame)
        vad_res = vad.process_frame(pcm_frame)

        if vad_res["event"] == "speech_finalize" or vad_res["event"] == "speech_start":
            if vad_res["pcm"]:
                speech_chunks.append(vad_res["pcm"])

    if not speech_chunks:
        speech_chunks.append(speech_pcm)

    assembled_pcm = chunker.assemble_utterance(b"".join(speech_chunks))

    quality = quality_monitor.evaluate_pcm(assembled_pcm)
    print(f"Audio Quality State : {quality.state.value}")
    print(f"RMS Energy          : {quality.rms_db} dBFS")
    print(f"Clipping %          : {quality.clipping_percent}%")
    print(f"Advice              : {quality.actionable_advice}")
    print("--------------------------------------------------")

    print("Transcribing PCM buffer with SpeechTranscriber...")
    end_time = start_time + int(duration_s * 1000)
    event = await transcriber.transcribe_pcm_chunk(
        pcm16=assembled_pcm,
        session_id=session_id,
        started_ms=start_time,
        ended_ms=end_time,
        input_mode="replay",
    )

    if event:
        print("✅ TranscriptEvent Emitted Successfully:")
        print(f"  Utterance ID   : {event.utterance_id}")
        print(f"  Session ID     : {event.session_id}")
        print(f"  Text           : {event.text}")
        print(f"  Language       : {event.language}")
        print(f"  Confidence     : {event.asr_confidence}")
        print(f"  Input Mode     : {event.input_mode}")
    else:
        print("❌ Transcription failed to emit event.")

    print("==================================================")


if __name__ == "__main__":
    asyncio.run(main())
