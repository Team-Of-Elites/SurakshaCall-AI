# Rajyavardhan Backend and Orchestration Handoff

This implementation creates the local FastAPI backend backbone for SurakshaCall AI.

## What is included

- FastAPI application factory in `backend/app/main.py`.
- Local settings loader in `backend/app/config.py`.
- Lifespan startup and graceful worker shutdown in `backend/app/lifespan.py`.
- Shared Pydantic schemas for events, transcript, evidence, identity, and risk decisions.
- Isolated `CallState` per session with transcript windowing and reset/end behavior.
- Queue-based transcript processing through `SessionWorker`.
- Deterministic orchestration flow for fast detection, deep-analysis triggers, identity fallback, community fallback, and risk updates.
- Dashboard and mobile WebSocket endpoints with reconnect snapshots.
- HTTP routes for health, sessions, microphone start, replay validation, caller metadata, reset, end, and transcript ingestion.
- Local fallback detector contract so the backend can run before the full classifier is integrated.

## Run locally

```bash
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

Create a session:

```bash
curl -X POST http://127.0.0.1:8000/api/sessions
```

Send a final transcript after replacing `<session_id>`:

```bash
curl -X POST http://127.0.0.1:8000/api/sessions/<session_id>/transcript-final \
  -H "Content-Type: application/json" \
  -d '{"text":"Please share your OTP right now.","speaker":"unknown"}'
```

## Endpoint checklist

- `GET /api/health`
- `POST /api/sessions`
- `GET /api/sessions/{session_id}`
- `POST /api/sessions/{session_id}/start-microphone`
- `POST /api/sessions/{session_id}/start-replay`
- `POST /api/sessions/{session_id}/end`
- `POST /api/sessions/{session_id}/reset`
- `POST /api/sessions/{session_id}/caller-metadata`
- `POST /api/sessions/{session_id}/analyze-now`
- `POST /api/sessions/{session_id}/transcript-final`
- `WS /ws/dashboard/{session_id}`
- `WS /ws/mobile/{session_id}`

## Integration notes

- Odil can post final ASR output to `transcript-final`; later this can be replaced by direct queue submission.
- Lakshay can replace `backend/app/detection/service.py` while keeping the same `detect(text)` contract.
- Mayank can plug database/community repositories into the orchestration graph without changing WebSocket contracts.
- Namit can replace `aggregate_decision` with the final risk decision engine while keeping the `RiskDecision` schema stable.
- Palak can consume WebSocket event envelopes and reconnect snapshots from dashboard/mobile sockets.

## Verification

```bash
python -m pytest tests/test_backend_sessions.py tests/test_rules.py -q
python -m compileall backend/app -q
```
