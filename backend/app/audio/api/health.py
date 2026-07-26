from fastapi import APIRouter, Request

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health(request: Request) -> dict:
    sessions = request.app.state.session_manager
    settings = request.app.state.settings
    diagnostics = request.app.state.diagnostics
    return {
        "backend": "ok",
        "database": diagnostics.get("database", "memory-only"),
        "whisper": diagnostics.get("whisper", "not_started"),
        "local_llm": diagnostics.get("local_llm", "not_required"),
        "microphone": diagnostics.get("microphone", "not_started"),
        "active_sessions": sum(
            1 for state in sessions.sessions.values() if state.status == "active"
        ),
        "mode": "local-network" if settings.local_network_mode else "local",
        "websocket_clients": request.app.state.websocket_manager.counts(),
    }
