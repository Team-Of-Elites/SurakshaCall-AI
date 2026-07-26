from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.app.schemas.events import EventType, make_event

router = APIRouter()


@router.websocket("/ws/mobile/{session_id}")
async def mobile_socket(websocket: WebSocket, session_id: str) -> None:
    manager = websocket.app.state.websocket_manager
    sessions = websocket.app.state.session_manager
    await manager.connect(session_id, "mobile", websocket)
    state = sessions.get_session(session_id)
    if state:
        await websocket.send_text(
            make_event(EventType.SESSION_SNAPSHOT, session_id, sessions.snapshot(state)).model_dump_json()
        )
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id, "mobile", websocket)
