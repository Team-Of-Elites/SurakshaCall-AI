from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from backend.app.config import get_settings
from backend.app.schemas.events import EventType, make_event

router = APIRouter()


@router.websocket("/ws/dashboard/{session_id}")
async def dashboard_socket(websocket: WebSocket, session_id: str) -> None:
    token = websocket.query_params.get("token", "")
    settings = get_settings()
    if settings.session_token and token != settings.session_token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or missing session token")
        return

    manager = websocket.app.state.websocket_manager
    sessions = websocket.app.state.session_manager
    await manager.connect(session_id, "dashboard", websocket)
    state = sessions.get_session(session_id)
    if state:
        await websocket.send_text(
            make_event(EventType.SESSION_SNAPSHOT, session_id, sessions.snapshot(state)).model_dump_json()
        )
    else:
        await websocket.send_text(
            make_event(
                EventType.SYSTEM_ERROR,
                session_id,
                {"message": "Session not found. Create a new session and reconnect."},
            ).model_dump_json()
        )
        manager.disconnect(session_id, "dashboard", websocket)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id, "dashboard", websocket)
