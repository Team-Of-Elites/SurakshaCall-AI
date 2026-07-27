from fastapi import APIRouter, Request

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health(request: Request) -> dict:
    sessions = request.app.state.session_manager
    settings = request.app.state.settings
    diagnostics = request.app.state.diagnostics
    database_status = _database_status()
    whisper_status = _whisper_status()
    llm_status = _llm_status(sessions, settings)
    diagnostics["database"] = database_status
    diagnostics["whisper"] = whisper_status
    diagnostics["local_llm"] = llm_status
    return {
        "backend": "ok",
        "database": database_status,
        "whisper": whisper_status,
        "local_llm": llm_status,
        "microphone": diagnostics.get("microphone", "not_started"),
        "active_sessions": sum(
            1 for state in sessions.sessions.values() if state.status == "active"
        ),
        "mode": "local-network" if settings.local_network_mode else "local",
        "websocket_clients": request.app.state.websocket_manager.counts(),
    }


def _database_status() -> str:
    try:
        from backend.app.database.connection import get_connection

        conn = get_connection()
        try:
            conn.execute("SELECT 1")
        finally:
            conn.close()
        return "ok"
    except Exception:
        return "memory-only"


def _whisper_status() -> str:
    try:
        import faster_whisper  # noqa: F401

        return "ready"
    except Exception:
        return "not_installed"


def _llm_status(sessions, settings=None) -> str:
    if settings is not None and not getattr(settings, "local_llm_enabled", False):
        return "disabled_rules_only"
    try:
        import ollama  # noqa: F401
    except Exception:
        return "rules-only"
    if any(not state.llm_available for state in sessions.sessions.values()):
        return "rules-only"
    return "ready"
