"""
scripts/benchmark_whisper.py — Task O-07 GPU/CPU Benchmarking CLI Tool

Measures faster-whisper inference speed, Real-Time Factor (RTF), and memory latency.
Usage:
    python scripts/benchmark_whisper.py
"""

import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.stt.model_loader import WhisperModelLoader
from backend.app.stt.transcriber import pcm_to_wav_bytes


def main():
    print("==================================================")
    print("  SurakshaCall AI — faster-whisper Benchmark")
    print("==================================================")

    sample_rate = 16000
    duration_s = 5.0
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), False)
    sine_wave = (np.sin(2 * np.pi * 440 * t) * 16384).astype(np.int16)
    pcm_bytes = sine_wave.tobytes()
    wav_bytes = pcm_to_wav_bytes(pcm_bytes, sample_rate)

    print("Attempting model load (CUDA float16 -> CPU int8 fallback)...")
    start_load = time.perf_counter()
    model, device, compute_type = WhisperModelLoader.get_model(
        model_size="small",
        preferred_device="cuda",
        preferred_compute_type="float16",
    )
    load_time = time.perf_counter() - start_load

    print(f"Loaded Model Device: {device.upper()} ({compute_type}) in {load_time:.2f}s")
    if model is None:
        print("❌ Model failed to load.")
        return

    import io
    print(f"Running inference on {duration_s:.1f}s test audio chunk...")
    start_infer = time.perf_counter()
    segments, info = model.transcribe(io.BytesIO(wav_bytes), beam_size=1)
    _text = " ".join(s.text for s in segments)
    infer_duration = time.perf_counter() - start_infer

    rtf = infer_duration / duration_s
    print("--------------------------------------------------")
    print(f"  Inference Time : {infer_duration * 1000:.2f} ms")
    print(f"  Audio Duration : {duration_s:.1f} s")
    print(f"  Real-Time Factor (RTF): {rtf:.4f} (Lower is faster)")
    if rtf < 1.0:
        print(f"  Speedup Factor : {1.0 / rtf:.2f}x faster than real-time")
    print("==================================================")


if __name__ == "__main__":
    main()
