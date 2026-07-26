from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.audio.queues import AudioQueueRegistry
from backend.app.audio.transcriber import MobileAudioTranscriptionService
from backend.app.api.mobile_pairing import make_mobile_pusher
from backend.app.config import get_settings
from backend.app.orchestration.sessions import SessionManager
from backend.app.websocket.manager import WebSocketManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.websocket_manager = WebSocketManager(settings.websocket_max_payload_bytes)
    app.state.session_manager = SessionManager(settings, app.state.websocket_manager)
    app.state.session_manager.mobile_pusher = make_mobile_pusher(
        app.state.websocket_manager
    )
    app.state.audio_queues = AudioQueueRegistry(settings.max_queue_size)
    app.state.mobile_audio_transcriber = MobileAudioTranscriptionService(
        settings=settings,
        audio_queues=app.state.audio_queues,
        sessions=app.state.session_manager,
    )
    app.state.diagnostics = {
        "database": "memory-only",
        "whisper": "not_started",
        "local_llm": "not_required",
        "microphone": "not_started",
    }
    yield
    await app.state.mobile_audio_transcriber.shutdown()
    await app.state.session_manager.shutdown()
