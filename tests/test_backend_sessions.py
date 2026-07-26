from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_health_works_without_llm():
    with TestClient(create_app()) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["backend"] == "ok"


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
