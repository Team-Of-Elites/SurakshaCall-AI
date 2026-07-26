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


def build_mobile_url(request: Request, session_id: str) -> str:
    settings = request.app.state.settings
    host = get_local_ip() if settings.local_network_mode else settings.host
    return f"https://{host}:{settings.port}/mobile/{session_id}"


def build_mobile_ws_url(request: Request, session_id: str) -> str:
    settings = request.app.state.settings
    host = get_local_ip() if settings.local_network_mode else settings.host
    return f"wss://{host}:{settings.port}/ws/mobile/{session_id}"


@router.get("/mobile/{session_id}", response_class=HTMLResponse)
async def mobile_page(session_id: str) -> HTMLResponse:
    html_path = Path(__file__).resolve().parents[3] / "frontend" / "mobile.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="mobile.html not found")
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
        note="Open the HTTPS pairing URL on the phone and accept the self-signed certificate once before demo.",
    )


@router.websocket("/ws/mobile/{session_id}")
async def mobile_audio_socket(websocket: WebSocket, session_id: str) -> None:
    manager = websocket.app.state.websocket_manager
    sessions = websocket.app.state.session_manager
    audio_queues = websocket.app.state.audio_queues
    mobile_audio = websocket.app.state.mobile_audio_transcriber

    await manager.connect(session_id, "mobile", websocket)
    state = sessions.get_session(session_id)
    if state:
        mobile_audio.ensure_session(session_id)
        await websocket.send_text(
            make_event(EventType.SESSION_SNAPSHOT, session_id, sessions.snapshot(state)).model_dump_json()
        )
    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break
            if "bytes" in message and message["bytes"] is not None:
                if sessions.get_session(session_id) is None:
                    continue
                await audio_queues.put_mobile_pcm(session_id, message["bytes"])
            elif "text" in message and message["text"]:
                await _handle_mobile_control(websocket, session_id, message["text"])
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(session_id, "mobile", websocket)
        await sessions.publish(
            make_event(
                EventType.AUDIO_STATUS,
                session_id,
                {"input_mode": "mobile", "status": "disconnected"},
            )
        )


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
    async def push_to_mobile(session_id: str, message: dict) -> None:
        event_type = EventType.DECISION_UPDATE if message.get("type") == "decision_update" else EventType.SAFETY_WARNING
        event = make_event(event_type, session_id, message)
        await websocket_manager.broadcast(event, kinds=("mobile",))

    return push_to_mobile


async def push_to_mobile(request_or_app, session_id: str, message: dict) -> None:
    app = getattr(request_or_app, "app", request_or_app)
    await make_mobile_pusher(app.state.websocket_manager)(session_id, message)
