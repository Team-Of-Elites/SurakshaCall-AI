"""
scripts/record_test_audio.py — Helper Tool

Records microphone input for a specified duration and saves to data/demo WAV file for timed replay.
Usage:
    python scripts/record_test_audio.py --duration 5 --output data/demo/test_scam_call.wav
"""

import sys
import os
import wave
import argparse
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.audio.devices import select_audio_device


def record_audio(output_path: str, duration: float = 5.0, sample_rate: int = 16000):
    try:
        import sounddevice as sd
    except ImportError:
        print("❌ sounddevice is not installed.")
        return

    dev_idx, dev_name = select_audio_device()
    print(f"Recording {duration:.1f}s from device: [{dev_idx}] {dev_name}...")
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        device=dev_idx,
    )
    sd.wait()
    print("Recording finished. Saving WAV file...")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Record test WAV file for timed replay.")
    parser.add_argument("--output", type=str, default="data/demo/test_recording.wav", help="Output WAV path")
    parser.add_argument("--duration", type=float, default=5.0, help="Duration in seconds")
    args = parser.parse_args()

    record_audio(args.output, args.duration)


if __name__ == "__main__":
    main()
