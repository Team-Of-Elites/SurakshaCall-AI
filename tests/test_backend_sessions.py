from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_health_works_without_llm():
    with TestClient(create_app()) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["backend"] == "ok"
    assert "database" in response.json()
    assert "whisper" in response.json()
    assert "local_llm" in response.json()


def test_session_lifecycle_and_transcript_ingestion():
    with TestClient(create_app()) as client:
        created = client.post("/api/sessions")
        assert created.status_code == 201
        session_id = created.json()["session"]["session_id"]

        started = client.post(f"/api/sessions/{session_id}/start-microphone")
        assert started.status_code == 200
        assert started.json()["session"]["input_mode"] == "microphone"

        transcript = client.post(
            f"/api/sessions/{session_id}/transcript-final",
            json={"text": "Please share your OTP right now.", "speaker": "unknown"},
        )
        assert transcript.status_code == 202
        assert transcript.json()["accepted"] is True

        analyze = client.post(f"/api/sessions/{session_id}/analyze-now")
        assert analyze.status_code == 200

        ended = client.post(f"/api/sessions/{session_id}/end")
        assert ended.status_code == 200
        assert ended.json()["session"]["status"] == "ended"


def test_deep_analysis_updates_decision_with_rules_fallback():
    with TestClient(create_app()) as client:
        session_id = client.post("/api/sessions").json()["session"]["session_id"]
        transcript = client.post(
            f"/api/sessions/{session_id}/transcript-final",
            json={
                "text": "This is the bank. Please share your OTP right now.",
                "speaker": "unknown",
            },
        )
        assert transcript.status_code == 202

        response = client.post(f"/api/sessions/{session_id}/analyze-now")
        assert response.status_code == 200
        session = response.json()["session"]
        assert session["current_risk"] >= 40
        assert session["risk_level"] in {"MEDIUM", "HIGH", "CRITICAL"}


def test_invalid_dashboard_websocket_gets_error():
    with TestClient(create_app()) as client:
        with client.websocket_connect("/ws/dashboard/not-a-session?token=local-dev-token") as websocket:
            message = websocket.receive_json()
            assert message["type"] == "system_error"


def test_replay_feeds_shared_transcription_queue(monkeypatch, tmp_path):
    import math
    import time
    import wave

    from backend.app.config import get_settings

    demo_dir = tmp_path / "demo"
    demo_dir.mkdir()
    wav_path = demo_dir / "sample.wav"
    sample_rate = 16_000
    samples = int(sample_rate * 0.35)
    audio = bytearray()
    for index in range(samples):
        value = int(math.sin(2 * math.pi * 440 * index / sample_rate) * 8000)
        audio.extend(value.to_bytes(2, byteorder="little", signed=True))

    with wave.open(str(wav_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(audio))

    monkeypatch.setenv("DEMO_AUDIO_DIR", str(demo_dir))
    monkeypatch.setenv("MOBILE_TEST_TRANSCRIPT", "replay transcript reached pipeline")
    monkeypatch.setenv("MOBILE_TRANSCRIPTION_CHUNK_SECONDS", "0.1")
    get_settings.cache_clear()

    with TestClient(create_app()) as client:
        session_id = client.post("/api/sessions").json()["session"]["session_id"]
        response = client.post(
            f"/api/sessions/{session_id}/start-replay",
            json={"file_name": "sample.wav", "speed": 4.0},
        )
        assert response.status_code == 200
        assert response.json()["replay"]["status"] == "queued"

        deadline = time.time() + 3
        session = {}
        while time.time() < deadline:
            session = client.get(f"/api/sessions/{session_id}").json()["session"]
            if session["recent_transcript"]:
                break
            time.sleep(0.05)

        assert session["recent_transcript"]
        assert session["recent_transcript"][-1]["text"] == "replay transcript reached pipeline"
