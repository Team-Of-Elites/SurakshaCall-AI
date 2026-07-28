from functools import lru_cache
import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "SurakshaCall AI Backend"
    environment: str = Field(default="local")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    local_network_mode: bool = Field(default=False)
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
    demo_audio_dir: str = Field(default="data/demo")
    max_queue_size: int = Field(default=100)
    transcript_window_seconds: int = Field(default=120)
    normal_interval_seconds: int = Field(default=10)
    high_risk_interval_seconds: int = Field(default=4)
    minimum_new_words: int = Field(default=12)
    llm_timeout_seconds: float = Field(default=6.0)
    structured_retry_count: int = Field(default=1)
    websocket_max_payload_bytes: int = Field(default=64_000)
    session_token: str = Field(default="local-dev-token")
    whisper_model: str = Field(default="small")
    whisper_device: str = Field(default="cpu")
    whisper_compute_type: str = Field(default="int8")
    llm_model: str = Field(default="qwen3:4b")
    clear_session_on_end: bool = Field(default=True)
    mobile_transcription_chunk_seconds: float = Field(default=1.0)
    test_transcript_override: str | None = Field(default=None)
    microphone_capture_enabled: bool = Field(default=False)
    local_llm_enabled: bool = Field(default=False)


def _bool_from_env(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _list_from_env(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    defaults = Settings()
    return Settings(
        environment=os.getenv("ENVIRONMENT", defaults.environment),
        host=os.getenv("BACKEND_HOST", defaults.host),
        port=int(os.getenv("BACKEND_PORT", str(defaults.port))),
        local_network_mode=_bool_from_env(
            os.getenv("LOCAL_NETWORK_MODE"), defaults.local_network_mode
        ),
        cors_origins=_list_from_env(os.getenv("CORS_ORIGINS"), defaults.cors_origins),
        demo_audio_dir=os.getenv("DEMO_AUDIO_DIR", defaults.demo_audio_dir),
        max_queue_size=int(os.getenv("MAX_QUEUE_SIZE", str(defaults.max_queue_size))),
        normal_interval_seconds=int(
            os.getenv("NORMAL_INTERVAL_SECONDS", str(defaults.normal_interval_seconds))
        ),
        high_risk_interval_seconds=int(
            os.getenv("HIGH_RISK_INTERVAL_SECONDS", str(defaults.high_risk_interval_seconds))
        ),
        minimum_new_words=int(
            os.getenv("MINIMUM_NEW_WORDS", str(defaults.minimum_new_words))
        ),
        llm_timeout_seconds=float(
            os.getenv("LLM_TIMEOUT_SECONDS", str(defaults.llm_timeout_seconds))
        ),
        structured_retry_count=int(
            os.getenv("STRUCTURED_RETRY_COUNT", str(defaults.structured_retry_count))
        ),
        session_token=os.getenv("SESSION_TOKEN", defaults.session_token),
        whisper_model=os.getenv("WHISPER_MODEL", defaults.whisper_model),
        llm_model=os.getenv("LLM_MODEL", defaults.llm_model),
        whisper_device=os.getenv("WHISPER_DEVICE", defaults.whisper_device),
        whisper_compute_type=os.getenv(
            "WHISPER_COMPUTE_TYPE", defaults.whisper_compute_type
        ),
        clear_session_on_end=_bool_from_env(
            os.getenv("CLEAR_SESSION_ON_END"), defaults.clear_session_on_end
        ),
        mobile_transcription_chunk_seconds=float(
            os.getenv(
                "MOBILE_TRANSCRIPTION_CHUNK_SECONDS",
                str(defaults.mobile_transcription_chunk_seconds),
            )
        ),
        test_transcript_override=os.getenv("MOBILE_TEST_TRANSCRIPT"),
        microphone_capture_enabled=_bool_from_env(
            os.getenv("MICROPHONE_CAPTURE_ENABLED"),
            defaults.microphone_capture_enabled,
        ),
        local_llm_enabled=_bool_from_env(
            os.getenv("LOCAL_LLM_ENABLED"),
            defaults.local_llm_enabled,
        ),
    )
