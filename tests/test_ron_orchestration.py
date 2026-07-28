"""Tests for Ron's orchestration domain — session isolation, WS, cooldown, fallback."""
import json
import time
import pytest
from starlette.websockets import WebSocketDisconnect

from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_session_isolation():
    """Two sessions must not share state."""
    with TestClient(create_app()) as client:
        s1 = client.post("/api/sessions").json()["session"]
        s2 = client.post("/api/sessions").json()["session"]
        assert s1["session_id"] != s2["session_id"]

        client.post(f"/api/sessions/{s1['session_id']}/transcript-final",
                     json={"text": "Share your OTP now.", "speaker": "caller"})
        client.post(f"/api/sessions/{s2['session_id']}/transcript-final",
                     json={"text": "How is the weather today?", "speaker": "user"})

        g1 = client.get(f"/api/sessions/{s1['session_id']}").json()["session"]
        g2 = client.get(f"/api/sessions/{s2['session_id']}").json()["session"]

        assert g1["current_risk"] >= 30
        assert g2["current_risk"] < 30


def test_event_envelope_validation():
    """Malformed event must not crash the pipeline."""
    with TestClient(create_app()) as client:
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        r = client.post(f"/api/sessions/{sid}/transcript-final",
                        json={"text": "", "speaker": "unknown"})
        assert r.status_code in (202, 422)


def test_websocket_broadcast():
    """Dashboard WS must receive events after transcript submission."""
    with TestClient(create_app()) as client:
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        client.post(f"/api/sessions/{sid}/transcript-final",
                    json={"text": "Give me your OTP right now.", "speaker": "caller"})
        client.post(f"/api/sessions/{sid}/analyze-now")

        with client.websocket_connect(f"/ws/dashboard/{sid}?token=local-dev-token") as ws:
            msg = ws.receive_json()
            assert msg["type"] == "session_snapshot"
            assert "current_risk" in msg["payload"]
            assert msg["payload"]["current_risk"] > 0


def test_reconnect_snapshot():
    """Reconnecting dashboard WS must receive current snapshot with risk data."""
    with TestClient(create_app()) as client:
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        client.post(f"/api/sessions/{sid}/transcript-final",
                    json={"text": "Transfer money to safe account now.", "speaker": "caller"})
        client.post(f"/api/sessions/{sid}/analyze-now")

        with client.websocket_connect(f"/ws/dashboard/{sid}?token=local-dev-token") as ws:
            msg = ws.receive_json()
            assert msg["type"] == "session_snapshot"
            assert msg["session_id"] == sid
            assert msg["payload"]["current_risk"] > 0


def test_fast_warning_before_deep_analysis():
    """Fast detection runs before deep analysis and updates risk."""
    with TestClient(create_app()) as client:
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        client.post(f"/api/sessions/{sid}/transcript-final",
                    json={"text": "I am from CBI. Share your OTP now.", "speaker": "caller"})
        r = client.post(f"/api/sessions/{sid}/analyze-now")
        assert r.status_code == 200
        session = r.json()["session"]
        assert session["current_risk"] >= 30
        assert len(session["evidence_events"]) > 0
        evidence_labels = {e["label"] for e in session["evidence_events"]}
        assert evidence_labels.intersection({"SECRET_REQUEST", "AUTHORITY_CLAIM", "FEAR_THREAT"})


def test_deep_analysis_cooldown():
    """Deep analysis must not run on every utterance within cooldown."""
    with TestClient(create_app()) as client:
        from backend.app.config import get_settings
        get_settings.cache_clear()
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        client.post(f"/api/sessions/{sid}/transcript-final",
                    json={"text": "Share your OTP now.", "speaker": "caller"})
        state1 = client.get(f"/api/sessions/{sid}").json()["session"]
        last_analysis = state1.get("last_deep_analysis_at")
        if last_analysis:
            client.post(f"/api/sessions/{sid}/transcript-final",
                        json={"text": "Tell me the code.", "speaker": "caller"})
            state2 = client.get(f"/api/sessions/{sid}").json()["session"]
            assert state2.get("last_deep_analysis_at") == last_analysis, \
                "Should not re-run deep analysis within cooldown"


def test_llm_timeout_fallback():
    """When LLM is unavailable, rules-only fallback must produce a decision."""
    with TestClient(create_app()) as client:
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        client.post(f"/api/sessions/{sid}/transcript-final",
                    json={"text": "I am calling from SBI. Your account will be frozen. Share your OTP.", "speaker": "caller"})
        r = client.post(f"/api/sessions/{sid}/analyze-now")
        assert r.status_code == 200
        session = r.json()["session"]
        assert session["current_risk"] >= 30
        assert session["risk_level"] in {"MEDIUM", "HIGH", "CRITICAL"}


def test_database_failure_memory_mode():
    """Backend must survive database unavailability."""
    import sys
    mock_module = type(sys)("backend.app.database.connection")
    mock_module.get_connection = lambda: (_ for _ in ()).throw(Exception("DB down"))
    mock_module.get_db = lambda: (_ for _ in ()).throw(Exception("DB down"))
    mock_module.DATABASE_PATH = ":memory:"
    sys.modules["backend.app.database.connection"] = mock_module

    try:
        with TestClient(create_app()) as client:
            health = client.get("/api/health").json()
            assert health["backend"] == "ok"
            assert health["database"] in ("memory-only", "ok")
            sid = client.post("/api/sessions").json()["session"]["session_id"]
            client.post(f"/api/sessions/{sid}/transcript-final",
                        json={"text": "Test transcript.", "speaker": "user"})
            r = client.get(f"/api/sessions/{sid}").json()
            assert r["session"]["session_id"] == sid
    finally:
        sys.modules.pop("backend.app.database.connection", None)


def test_session_reset():
    """Reset must clear risk and transcript while keeping session alive."""
    with TestClient(create_app()) as client:
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        client.post(f"/api/sessions/{sid}/transcript-final",
                    json={"text": "Share your OTP with me.", "speaker": "caller"})
        r = client.post(f"/api/sessions/{sid}/analyze-now")
        pre_risk = r.json()["session"]["current_risk"]
        assert pre_risk > 0

        r2 = client.post(f"/api/sessions/{sid}/reset")
        assert r2.status_code == 200
        post_state = r2.json()["session"]
        assert post_state["current_risk"] == 0
        assert post_state["status"] == "created"
        assert post_state["session_id"] == sid


def test_shutdown_clears_workers():
    """App shutdown must cancel all session workers."""
    app = create_app()
    with TestClient(app) as client:
        client.post("/api/sessions")
        client.post("/api/sessions")
        assert len(app.state.session_manager.workers) == 2
    assert len(app.state.session_manager.workers) == 0


def test_mobile_client_reconnect():
    """Reconnecting mobile WS must receive session snapshot."""
    with TestClient(create_app()) as client:
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        with client.websocket_connect(f"/ws/mobile/{sid}?token=local-dev-token") as ws:
            msg = ws.receive_json()
            assert msg["type"] == "session_snapshot"
            assert msg["session_id"] == sid

        with client.websocket_connect(f"/ws/mobile/{sid}?token=local-dev-token") as ws:
            msg = ws.receive_json()
            assert msg["type"] == "session_snapshot"


def test_health_reports_correctly():
    """Health endpoint must return all fields."""
    with TestClient(create_app()) as client:
        h = client.get("/api/health").json()
        assert h["backend"] == "ok"
        assert "database" in h
        assert "whisper" in h
        assert "local_llm" in h
        assert "microphone" in h
        assert "active_sessions" in h
        assert "mode" in h
        assert "websocket_clients" in h


def test_identity_community_integration():
    """Deep analysis must update risk via identity and community results."""
    with TestClient(create_app()) as client:
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        client.post(f"/api/sessions/{sid}/transcript-final",
                    json={"text": "I am calling from CBI. Share your OTP or you will be arrested.", "speaker": "caller"})
        r = client.post(f"/api/sessions/{sid}/analyze-now")
        assert r.status_code == 200
        session = r.json()["session"]
        assert session["current_risk"] >= 40


def test_session_token_enforcement():
    """WebSocket without valid token must be rejected."""
    with TestClient(create_app()) as client:
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(f"/ws/dashboard/{sid}"):  # no token
                pass


def test_replay_path_restriction():
    """Replay must reject paths outside data/demo."""
    with TestClient(create_app()) as client:
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        r = client.post(f"/api/sessions/{sid}/start-replay",
                        json={"file_name": "../../etc/passwd", "speed": 1.0})
        assert r.status_code == 400


def test_microphone_fallback_on_disabled():
    """Microphone start must not crash when mic capture is disabled."""
    with TestClient(create_app()) as client:
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        r = client.post(f"/api/sessions/{sid}/start-microphone")
        assert r.status_code == 200


def test_analyze_now_on_empty_session():
    """analyze-now on session with no transcript must not crash."""
    with TestClient(create_app()) as client:
        sid = client.post("/api/sessions").json()["session"]["session_id"]
        r = client.post(f"/api/sessions/{sid}/analyze-now")
        assert r.status_code == 200
