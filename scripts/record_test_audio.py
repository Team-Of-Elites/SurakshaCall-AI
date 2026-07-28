"""
scripts/record_test_audio.py — Helper Tool

Records microphone input for a specified duration, boosts quiet volume if needed,
and saves to data/demo WAV file for live testing.
Usage:
    python scripts/record_test_audio.py --duration 5 --output data/demo/live_mic_test.wav --device 1
"""

import sys
import os
import wave
import argparse
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.audio.devices import select_audio_device


def record_audio(output_path: str, duration: float = 5.0, sample_rate: int = 16000, device_index: int | None = None):
    try:
        import sounddevice as sd
    except ImportError:
        print("[ERROR] sounddevice is not installed.")
        return

    dev_idx, dev_name = select_audio_device(device_index)
    print(f"Recording {duration:.1f}s from device: [{dev_idx}] {dev_name}...")
    print("Speak clearly into your microphone now...")

    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        device=dev_idx,
    )
    sd.wait()

    arr = audio_data.flatten()
    peak = np.max(np.abs(arr))
    rms = np.sqrt(np.mean(arr.astype(float) ** 2))
    print(f"Recording finished. Peak amplitude: {peak}, RMS: {rms:.1f}")

    # Auto-boost low volume audio
    if peak > 50 and peak < 5000:
        gain = 15000.0 / float(peak)
        print(f"[INFO] Auto-boosting low microphone volume (Gain factor: {gain:.1f}x)...")
        boosted = np.clip(arr.astype(float) * gain, -32768, 32767).astype(np.int16)
        audio_bytes = boosted.tobytes()
    elif peak <= 50:
        print("[WARNING] Very low/zero audio detected. Make sure your mic is unmuted or try a different --device index.")
        audio_bytes = audio_data.tobytes()
    else:
        audio_bytes = audio_data.tobytes()

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)

    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Record test WAV file for timed replay.")
    parser.add_argument("--output", type=str, default="data/demo/live_mic_test.wav", help="Output WAV path")
    parser.add_argument("--duration", type=float, default=5.0, help="Duration in seconds")
    parser.add_argument("--device", type=int, default=None, help="Microphone device index")
    args = parser.parse_args()

    record_audio(args.output, args.duration, device_index=args.device)


if __name__ == "__main__":
    main()
