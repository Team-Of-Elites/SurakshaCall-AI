"""
scripts/list_microphones.py — Task O-02 CLI Tool

Lists available microphone input devices on host machine.
Usage:
    python scripts/list_microphones.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.audio.devices import list_input_devices, select_audio_device


def main():
    print("==================================================")
    print("  SurakshaCall AI — Audio Input Device Enumeration")
    print("==================================================")
    devices = list_input_devices()
    if not devices:
        print("❌ No input devices found!")
        return

    for dev in devices:
        is_def = " [DEFAULT]" if dev.get("is_default") else ""
        print(f"  [{dev['index']}] {dev['name']} (Channels: {dev['channels']}, Rate: {dev['default_samplerate']} Hz){is_def}")

    selected_idx, selected_name = select_audio_device()
    print("--------------------------------------------------")
    print(f"Active Selected Device: [{selected_idx}] {selected_name}")
    print("==================================================")


if __name__ == "__main__":
    main()
