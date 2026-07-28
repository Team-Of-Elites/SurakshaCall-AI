import json
import socket
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.app.schemas.events import EventType, make_event

router = APIRouter(tags=["mobile-pairing"])


class PairingResponse(BaseModel):
    session_id: str
    pairing_url: str
    websocket_url: str
    note: str


def get_local_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            probe.connect(("8.8.8.8", 80))
            return probe.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def resolve_host(request: Request) -> str:
    settings = request.app.state.settings
    if settings.local_network_mode or settings.host in {"127.0.0.1", "0.0.0.0", "localhost"}:
        local_ip = get_local_ip()
        if local_ip != "127.0.0.1":
            return local_ip
        req_host = request.url.hostname
        if req_host and req_host not in {"127.0.0.1", "localhost"}:
            return req_host
        return local_ip
    return settings.host


def build_mobile_url(request: Request, session_id: str) -> str:
    settings = request.app.state.settings
    host = resolve_host(request)
    scheme = request.url.scheme
    return f"{scheme}://{host}:{settings.port}/mobile/{session_id}"


def build_mobile_ws_url(request: Request, session_id: str) -> str:
    settings = request.app.state.settings
    host = resolve_host(request)
    scheme = "wss" if request.url.scheme == "https" else "ws"
    return f"{scheme}://{host}:{settings.port}/ws/mobile/{session_id}"


@router.get("/mobile/{session_id}", response_class=HTMLResponse)
async def mobile_page(request: Request, session_id: str) -> HTMLResponse:
    html_path = Path(__file__).resolve().parents[3] / "frontend" / "mobile.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="mobile.html not found")
    sessions = request.app.state.session_manager
    state = sessions.get_session(session_id)
    if state is None:
        print(f"MOBILE_PAGE: creating session {session_id}", flush=True)
        from backend.app.orchestration.state import CallState
        from datetime import datetime, timezone
        state = CallState(session_id=session_id)
        sessions.sessions[session_id] = state
        sessions._ensure_worker(state)
    html = html_path.read_text(encoding="utf-8").replace("__SESSION_ID__", session_id)
    return HTMLResponse(html)


@router.get("/api/v1/sessions/{session_id}/qr")
async def session_qr_code(request: Request, session_id: str) -> PairingResponse:
    if request.app.state.session_manager.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return PairingResponse(
        session_id=session_id,
        pairing_url=build_mobile_url(request, session_id),
        websocket_url=build_mobile_ws_url(request, session_id),
        note="Open the HTTP pairing URL on the phone.",
    )


@router.get("/api/v1/sessions/{session_id}/mobile-debug")
async def mobile_debug(request: Request, session_id: str) -> dict:
    state = request.app.state.session_manager.get_session(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session_id,
        "queue_sizes": request.app.state.audio_queues.sizes(),
        "recent_transcript_count": len(state.transcript_window),
        "recent_transcript": [
            item.model_dump(mode="json") for item in state.transcript_window[-5:]
        ],
        "mobile_transcriber": request.app.state.mobile_audio_transcriber.stats(),
    }


@router.websocket("/ws/mobile/{session_id}")
async def mobile_audio_socket(websocket: WebSocket, session_id: str) -> None:
    print(f"MOBILE_WS: connecting session={session_id}", flush=True)
    manager = websocket.app.state.websocket_manager
    sessions = websocket.app.state.session_manager
    audio_queues = websocket.app.state.audio_queues
    mobile_audio = websocket.app.state.mobile_audio_transcriber

    await manager.connect(session_id, "mobile", websocket)
    print(f"MOBILE_WS: accepted session={session_id}", flush=True)

    state = sessions.get_session(session_id)
    if state is None:
        print(f"MOBILE_WS: session NOT FOUND {session_id}", flush=True)
        await websocket.send_text(
            make_event(EventType.SYSTEM_ERROR, session_id, {
                "message": "Session not found. Create a session first."
            }).model_dump_json()
        )
        manager.disconnect(session_id, "mobile", websocket)
        await websocket.close(code=1008)
        return

    print(f"MOBILE_WS: session FOUND {session_id}", flush=True)
    state.input_mode = "mobile"
    state.status = "active"
    mobile_audio.ensure_session(session_id)
    await websocket.send_text(
        make_event(EventType.SESSION_SNAPSHOT, session_id, sessions.snapshot(state)).model_dump_json()
    )
    print(f"MOBILE_WS: snapshot sent for {session_id}", flush=True)

    try:
        while True:
            message = await websocket.receive()
            msg_type = message.get("type", "")
            print(f"MOBILE_WS: received type={msg_type} session={session_id}", flush=True)

            if msg_type == "websocket.disconnect":
                print(f"MOBILE_WS: client disconnect {session_id}", flush=True)
                break

            if "bytes" in message and message.get("bytes"):
                data = message["bytes"]
                print(f"MOBILE_WS: audio frame {len(data)} bytes session={session_id}", flush=True)
                if sessions.get_session(session_id) is None:
                    continue
                await audio_queues.put_mobile_pcm(session_id, data)

            elif "text" in message and message.get("text"):
                text = message["text"]
                print(f"MOBILE_WS: text message session={session_id}", flush=True)
                await _handle_mobile_control(websocket, session_id, text)

    except WebSocketDisconnect:
        print(f"MOBILE_WS: WebSocketDisconnect {session_id}", flush=True)
    except Exception as exc:
        print(f"MOBILE_WS: ERROR session={session_id} exc={exc}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        print(f"MOBILE_WS: cleanup session={session_id}", flush=True)
        manager.disconnect(session_id, "mobile", websocket)
        await sessions.publish(
            make_event(EventType.AUDIO_STATUS, session_id, {
                "input_mode": "mobile", "status": "disconnected"
            })
        )
        print(f"MOBILE_WS: done session={session_id}", flush=True)


async def _handle_mobile_control(websocket: WebSocket, session_id: str, text: str) -> None:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = {"type": "unknown"}
    if payload.get("type") == "ping":
        await websocket.send_text(
            make_event(EventType.SYSTEM_STATUS, session_id, {"mobile": "pong"}).model_dump_json()
        )


def make_mobile_pusher(websocket_manager):
    async def push_to_mobile(
        session_id: str,
        message: dict,
        event_type: EventType = EventType.SAFETY_WARNING,
    ) -> None:
        event = make_event(event_type, session_id, message)
        await websocket_manager.broadcast(event, kinds=("mobile",))
    return push_to_mobile


async def push_to_mobile(request_or_app, session_id: str, message: dict) -> None:
    app = getattr(request_or_app, "app", request_or_app)
    await make_mobile_pusher(app.state.websocket_manager)(session_id, message)
