"""
scripts/test_live_transcription.py

Transcribes recorded live mic audio file (data/demo/live_mic_test.wav) using SpeechTranscriber.
Usage:
    py scripts/test_live_transcription.py
"""

import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.audio.replay import TimedReplayEngine
from backend.app.stt.transcriber import SpeechTranscriber


async def main():
    wav_path = "data/demo/live_mic_test.wav"
    if not os.path.exists(wav_path):
        print(f"[ERROR] File not found: {wav_path}")
        print("Please run: py scripts/record_test_audio.py --duration 5 --output data/demo/live_mic_test.wav first.")
        return

    print("==================================================")
    print("  Transcribing Live Recorded Audio...")
    print("==================================================")

    engine = TimedReplayEngine()
    transcriber = SpeechTranscriber()

    pcm, sample_rate, channels = engine.validate_and_load_wav(wav_path)
    now_ms = int(time.time() * 1000)
    duration_ms = int((len(pcm) / (sample_rate * channels * 2)) * 1000)

    event = await transcriber.transcribe_pcm_chunk(
        pcm16=pcm,
        session_id="live_mic_session",
        started_ms=now_ms - duration_ms,
        ended_ms=now_ms,
        input_mode="microphone",
        sample_rate=sample_rate,
    )

    print("--------------------------------------------------")
    if event and event.text:
        print("[OK] TRANSCRIPTION RESULT:")
        print(f"  Utterance ID : {event.utterance_id}")
        print(f"  Text         : {event.text}")
        print(f"  Language     : {event.language}")
        print(f"  Confidence   : {event.asr_confidence:.2f}")
    else:
        print("[NOTICE] No speech recognized in recorded audio (audio was silent or background noise only).")
        print("Tip: Speak clearly into your mic during the 5-second recording!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(main())
