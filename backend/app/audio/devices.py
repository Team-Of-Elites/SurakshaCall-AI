"""
devices.py — Task O-02: Microphone Enumeration & Selection

Provides functionality to discover, inspect, select, and validate host audio input devices.
Falls back safely to system defaults or virtual mock devices if no physical microphone is available.
"""

import os
from typing import Any


def list_input_devices() -> list[dict[str, Any]]:
    """
    Enumerates host audio input devices using sounddevice.
    Returns a list of dictionary metadata for available input devices.
    """
    devices = []
    try:
        import sounddevice as sd
        device_list = sd.query_devices()
        for idx, dev in enumerate(device_list):
            if dev.get("max_input_channels", 0) > 0:
                devices.append({
                    "index": idx,
                    "name": dev.get("name", f"Device {idx}"),
                    "channels": dev.get("max_input_channels", 1),
                    "default_samplerate": dev.get("default_samplerate", 16000.0),
                    "is_default": idx == sd.default.device[0],
                })
    except Exception as exc:
        devices.append({
            "index": 0,
            "name": f"Default System Input (Fallback: {str(exc)})",
            "channels": 1,
            "default_samplerate": 16000.0,
            "is_default": True,
        })
    return devices


def select_audio_device(preferred_index: int | None = None) -> tuple[int | None, str]:
    """
    Resolves target input device index based on parameter, AUDIO_DEVICE_INDEX env var, or system default.
    Returns tuple of (device_index, device_name).
    """
    env_index = os.getenv("AUDIO_DEVICE_INDEX")
    target_idx = preferred_index
    if target_idx is None and env_index is not None:
        try:
            target_idx = int(env_index)
        except ValueError:
            target_idx = None

    devices = list_input_devices()
    if not devices:
        return None, "No input devices found"

    if target_idx is not None:
        matched = [d for d in devices if d["index"] == target_idx]
        if matched:
            return matched[0]["index"], matched[0]["name"]
        default_dev = next((d for d in devices if d.get("is_default")), devices[0])
        return default_dev["index"], f"{default_dev['name']} (Fallback from requested index {target_idx})"

    default_dev = next((d for d in devices if d.get("is_default")), devices[0])
    return default_dev["index"], default_dev["name"]
