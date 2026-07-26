import math
import time

from fastapi.testclient import TestClient

from backend.app.config import get_settings
from backend.app.main import create_app


def test_mobile_websocket_pcm_reaches_transcript_pipeline(monkeypatch):
    monkeypatch.setenv("MOBILE_TEST_TRANSCRIPT", "please share your otp right now")
    monkeypatch.setenv("MOBILE_TRANSCRIPTION_CHUNK_SECONDS", "0.1")
    get_settings.cache_clear()

    with TestClient(create_app()) as client:
        session_id = client.post("/api/sessions").json()["session"]["session_id"]

        with client.websocket_connect(f"/ws/mobile/{session_id}") as websocket:
            websocket.receive_json()
            websocket.send_bytes(_sine_pcm(seconds=0.25))

        deadline = time.time() + 2
        session = {}
        while time.time() < deadline:
            session = client.get(f"/api/sessions/{session_id}").json()["session"]
            if session["recent_transcript"]:
                break
            time.sleep(0.05)

        assert session["recent_transcript"]
        assert session["recent_transcript"][-1]["text"] == "please share your otp right now"


def _sine_pcm(seconds: float, sample_rate: int = 16_000) -> bytes:
    samples = int(seconds * sample_rate)
    output = bytearray()
    for index in range(samples):
        value = int(math.sin(2 * math.pi * 440 * index / sample_rate) * 8000)
        output.extend(value.to_bytes(2, byteorder="little", signed=True))
    return bytes(output)
