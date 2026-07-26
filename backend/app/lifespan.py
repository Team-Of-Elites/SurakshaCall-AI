from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.config import get_settings
from backend.app.orchestration.sessions import SessionManager
from backend.app.websocket.manager import WebSocketManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.websocket_manager = WebSocketManager(settings.websocket_max_payload_bytes)
    app.state.session_manager = SessionManager(settings, app.state.websocket_manager)
    app.state.diagnostics = {
        "database": "memory-only",
        "whisper": "not_started",
        "local_llm": "not_required",
        "microphone": "not_started",
    }
    yield
    await app.state.session_manager.shutdown()
