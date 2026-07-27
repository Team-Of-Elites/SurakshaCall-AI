from contextlib import suppress

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from backend.app.audio.microphone import MicrophoneCapture
from backend.app.orchestration.state import CallerMetadata
from backend.app.schemas.transcript import TranscriptIn

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class SessionResponse(BaseModel):
    session: dict


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_session(request: Request) -> SessionResponse:
    state = await request.app.state.session_manager.create_session()
    return SessionResponse(session=request.app.state.session_manager.snapshot(state))


@router.get("/{session_id}")
async def get_session(request: Request, session_id: str) -> SessionResponse:
    state = request.app.state.session_manager.get_session(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(session=request.app.state.session_manager.snapshot(state))


@router.post("/{session_id}/start-microphone")
async def start_microphone(request: Request, session_id: str) -> SessionResponse:
    try:
        state = await request.app.state.session_manager.start_mode(session_id, "microphone")
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None

    old_capture = request.app.state.microphone_captures.pop(session_id, None)
    if old_capture:
        old_capture.stop()

    request.app.state.mobile_audio_transcriber.ensure_session(session_id)
    loop = request.app.state.loop

    def on_frame(frame) -> None:
        loop.create_task(request.app.state.audio_queues.put_audio_frame(frame))

    if not request.app.state.settings.microphone_capture_enabled:
        request.app.state.diagnostics["microphone"] = "disabled_use_mobile_or_replay"
        return SessionResponse(session=request.app.state.session_manager.snapshot(state))

    capture = MicrophoneCapture(sample_rate=16000, channels=1)
    capture.start(session_id, on_frame, loop=loop)
    request.app.state.microphone_captures[session_id] = capture
    request.app.state.diagnostics["microphone"] = "ready" if capture.is_recording else "error"
    return SessionResponse(session=request.app.state.session_manager.snapshot(state))


@router.post("/{session_id}/end")
async def end_session(request: Request, session_id: str) -> SessionResponse:
    try:
        await _stop_audio_sources(request, session_id)
        state = await request.app.state.session_manager.end_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    return SessionResponse(session=request.app.state.session_manager.snapshot(state))


@router.post("/{session_id}/reset")
async def reset_session(request: Request, session_id: str) -> SessionResponse:
    try:
        await _stop_audio_sources(request, session_id)
        state = await request.app.state.session_manager.reset_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    return SessionResponse(session=request.app.state.session_manager.snapshot(state))


@router.post("/{session_id}/caller-metadata")
async def caller_metadata(request: Request, session_id: str, metadata: CallerMetadata) -> SessionResponse:
    try:
        state = await request.app.state.session_manager.update_caller_metadata(session_id, metadata)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    return SessionResponse(session=request.app.state.session_manager.snapshot(state))


@router.post("/{session_id}/analyze-now")
async def analyze_now(request: Request, session_id: str) -> SessionResponse:
    try:
        state = await request.app.state.session_manager.analyze_now(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    return SessionResponse(session=request.app.state.session_manager.snapshot(state))


@router.post("/{session_id}/transcript-final", status_code=status.HTTP_202_ACCEPTED)
async def transcript_final(request: Request, session_id: str, transcript: TranscriptIn) -> dict:
    try:
        utterance = await request.app.state.session_manager.submit_transcript(session_id, transcript)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    return {"accepted": True, "utterance_id": utterance.utterance_id}


async def _stop_audio_sources(request: Request, session_id: str) -> None:
    replay_task = request.app.state.replay_tasks.pop(session_id, None)
    if replay_task and not replay_task.done():
        replay_task.cancel()
        with suppress(asyncio.CancelledError):
            await replay_task
    capture = request.app.state.microphone_captures.pop(session_id, None)
    if capture:
        capture.stop()
    await request.app.state.mobile_audio_transcriber.stop_session(session_id)
