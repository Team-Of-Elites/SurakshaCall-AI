from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import health, mobile, mobile_pairing, replay, sessions
from backend.app.config import get_settings
from backend.app.lifespan import lifespan
from backend.app.websocket import dashboard


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(sessions.router)
    app.include_router(replay.router)
    app.include_router(mobile.router)
    app.include_router(mobile_pairing.router)
    app.include_router(dashboard.router)
    return app


app = create_app()
