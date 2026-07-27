import asyncio
from contextlib import suppress
from pathlib import Path
import wave

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from backend.app.audio.replay import TimedReplayEngine
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

    old_task = request.app.state.replay_tasks.pop(session_id, None)
    if old_task and not old_task.done():
        old_task.cancel()
        with suppress(asyncio.CancelledError):
            await old_task

    request.app.state.mobile_audio_transcriber.ensure_session(session_id)

    async def on_frame(frame) -> None:
        await request.app.state.audio_queues.put_audio_frame(frame)

    async def run_replay() -> None:
        engine = TimedReplayEngine()
        try:
            await request.app.state.session_manager.publish(
                make_event(EventType.AUDIO_STATUS, session_id, {
                    "input_mode": "replay",
                    "status": "streaming",
                    "file_name": replay.file_name,
                    "speed": replay.speed,
                    "duration_seconds": duration_seconds,
                })
            )
            await engine.start_replay(
                str(file_path),
                session_id=session_id,
                on_frame=on_frame,
                speed_factor=replay.speed,
            )
            await request.app.state.session_manager.publish(
                make_event(EventType.AUDIO_STATUS, session_id, {
                    "input_mode": "replay",
                    "status": "completed",
                    "file_name": replay.file_name,
                    "progress": 1.0,
                })
            )
        except asyncio.CancelledError:
            engine.stop()
            await request.app.state.session_manager.publish(
                make_event(EventType.AUDIO_STATUS, session_id, {
                    "input_mode": "replay",
                    "status": "stopped",
                    "file_name": replay.file_name,
                })
            )
            raise

    request.app.state.replay_tasks[session_id] = asyncio.create_task(run_replay())
    await request.app.state.session_manager.publish(
        make_event(EventType.AUDIO_STATUS, session_id, {
            "input_mode": "replay",
            "status": "queued",
            "file_name": replay.file_name,
            "speed": replay.speed,
            "duration_seconds": duration_seconds,
            "progress": 0.0,
        })
    )

    return {
        "session": request.app.state.session_manager.snapshot(state),
        "replay": {
            "file_name": replay.file_name,
            "speed": replay.speed,
            "duration_seconds": duration_seconds,
            "status": "queued",
        },
    }
