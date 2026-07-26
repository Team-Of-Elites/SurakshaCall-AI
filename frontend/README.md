# SurakshaCall AI Frontend

Static HTML, CSS, and JavaScript dashboard for managing the FastAPI backend.

## What It Provides

- Backend health check
- Session create, load, reset, end, and analyze controls
- Dashboard WebSocket connection to `/ws/dashboard/{session_id}`
- Caller metadata form
- Manual transcript submission to test detection
- Replay request form
- Phone pairing link loader
- Live risk, transcript, evidence, decision, and event views

## Run Locally

Start the backend from the repository root:

```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Start the frontend from this folder in a second terminal:

```bash
cd frontend
python -m http.server 5173 --bind 127.0.0.1
```

Open the dashboard:

```text
http://127.0.0.1:5173/
```

The dashboard defaults to:

```text
http://127.0.0.1:8000
```

as the backend base URL. Change it in the `Backend Base URL` field if your backend runs elsewhere.

## Basic Test Flow

1. Click `Check Health`.
2. Click `Create` to create a backend session.
3. Confirm the WebSocket status changes to connected, or click `Connect WS`.
4. Click `OTP Sample`.
5. Click `Submit Transcript`.
6. Confirm the risk panel updates and evidence appears.

## Phone Pairing

1. Create or load a session.
2. Click `Load Pairing`.
3. Open the generated phone URL on the phone.

The backend route is session-specific:

```text
/mobile/{session_id}
```

## Files

```text
frontend/
|-- index.html        # Main backend control dashboard
|-- mobile.html       # Phone microphone companion page served by backend
|-- css/
|   `-- app.css       # Dashboard styles
`-- js/
    `-- app.js        # REST and WebSocket client logic
```

## Troubleshooting

- If `Check Health` fails, confirm the backend is running on `http://127.0.0.1:8000`.
- If browser requests are blocked by CORS, serve the frontend from `http://127.0.0.1:5173` or add the frontend URL to `CORS_ORIGINS`.
- If WebSocket connection fails, create or load a valid session first.
- If phone pairing uses a LAN IP, run the backend with `--host 0.0.0.0` and use the laptop IP from the same Wi-Fi network.
