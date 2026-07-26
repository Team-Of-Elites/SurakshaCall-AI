from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

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
    request.app.state.diagnostics["microphone"] = "pending_audio_worker"
    return SessionResponse(session=request.app.state.session_manager.snapshot(state))


@router.post("/{session_id}/end")
async def end_session(request: Request, session_id: str) -> SessionResponse:
    try:
        state = await request.app.state.session_manager.end_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    return SessionResponse(session=request.app.state.session_manager.snapshot(state))


@router.post("/{session_id}/reset")
async def reset_session(request: Request, session_id: str) -> SessionResponse:
    try:
        state = await request.app.state.session_manager.reset_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    return SessionResponse(session=request.app.state.session_manager.snapshot(state))


@router.post("/{session_id}/caller-metadata")
async def caller_metadata(
    request: Request, session_id: str, metadata: CallerMetadata
) -> SessionResponse:
    try:
        state = await request.app.state.session_manager.update_caller_metadata(
            session_id, metadata
        )
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
async def transcript_final(
    request: Request, session_id: str, transcript: TranscriptIn
) -> dict:
    try:
        utterance = await request.app.state.session_manager.submit_transcript(
            session_id, transcript
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    return {"accepted": True, "utterance_id": utterance.utterance_id}
