from pathlib import Path
import wave

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from backend.app.schemas.events import EventType, make_event

router = APIRouter(prefix="/api/sessions", tags=["replay"])


class ReplayRequest(BaseModel):
    file_name: str
    speed: float = Field(default=1.0, gt=0, le=4.0)


@router.post("/{session_id}/start-replay")
async def start_replay(request: Request, session_id: str, replay: ReplayRequest) -> dict:
    settings = request.app.state.settings
    demo_dir = Path(settings.demo_audio_dir).resolve()
    file_path = (demo_dir / replay.file_name).resolve()
    if demo_dir not in file_path.parents or file_path.suffix.lower() != ".wav":
        raise HTTPException(status_code=400, detail="Replay must be a WAV file inside data/demo")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Replay file not found")
    try:
        with wave.open(str(file_path), "rb") as wav_file:
            frames = wav_file.getnframes()
            frame_rate = wav_file.getframerate()
            duration_seconds = frames / float(frame_rate)
    except wave.Error:
        raise HTTPException(status_code=400, detail="Invalid WAV file") from None

    try:
        state = await request.app.state.session_manager.start_mode(session_id, "replay")
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    await request.app.state.session_manager.publish(
        make_event(
            EventType.AUDIO_STATUS,
            session_id,
            {
                "input_mode": "replay",
                "status": "validated_pending_audio_worker",
                "file_name": replay.file_name,
                "speed": replay.speed,
                "duration_seconds": duration_seconds,
                "progress": 0.0,
            },
        )
    )

    return {
        "session": request.app.state.session_manager.snapshot(state),
        "replay": {
            "file_name": replay.file_name,
            "speed": replay.speed,
            "duration_seconds": duration_seconds,
            "status": "validated_pending_audio_worker",
        },
    }
