from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/mobile", tags=["mobile"])


@router.get("/{session_id}/connection")
async def mobile_connection(request: Request, session_id: str) -> dict:
    settings = request.app.state.settings
    state = request.app.state.session_manager.get_session(session_id)
    return {
        "session_id": session_id,
        "exists": state is not None,
        "backend_base_url": f"http://{settings.host}:{settings.port}",
        "mobile_ws": f"ws://{settings.host}:{settings.port}/ws/mobile/{session_id}",
        "privacy": "Local microphone or consented replay only. Raw audio is not saved by default.",
    }
