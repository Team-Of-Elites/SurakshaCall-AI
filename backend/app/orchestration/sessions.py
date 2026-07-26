from datetime import datetime, timezone
from uuid import uuid4

from backend.app.config import Settings
from backend.app.orchestration.state import CallerMetadata, CallState
from backend.app.orchestration.graph import run_deep_analysis
from backend.app.orchestration.worker import SessionWorker
from backend.app.schemas.events import EventEnvelope, EventType, make_event
from backend.app.schemas.transcript import TranscriptIn, Utterance


class SessionManager:
    def __init__(self, settings: Settings, websocket_manager) -> None:
        self.settings = settings
        self.websocket_manager = websocket_manager
        self.mobile_pusher = None
        self.sessions: dict[str, CallState] = {}
        self.workers: dict[str, SessionWorker] = {}

    async def create_session(self) -> CallState:
        session_id = str(uuid4())
        state = CallState(session_id=session_id)
        self.sessions[session_id] = state
        self._ensure_worker(state)
        await self.publish(make_event(EventType.SESSION_STARTED, session_id, self.snapshot(state)))
        return state

    def get_session(self, session_id: str) -> CallState | None:
        return self.sessions.get(session_id)

    async def reset_session(self, session_id: str) -> CallState:
        state = self.require_session(session_id)
        await self.stop_session_worker(session_id)
        state.reset_for_demo()
        self._ensure_worker(state)
        await self.publish(make_event(EventType.SESSION_RESET, session_id, self.snapshot(state)))
        return state

    async def end_session(self, session_id: str) -> CallState:
        state = self.require_session(session_id)
        state.status = "ended"
        state.ended_at = datetime.now(timezone.utc)
        await self.stop_session_worker(session_id)
        await self.publish(make_event(EventType.SESSION_ENDED, session_id, self.snapshot(state)))
        if self.settings.clear_session_on_end:
            state.transcript_window.clear()
            state.previous_summary = ""
        return state

    async def start_mode(self, session_id: str, mode: str) -> CallState:
        state = self.require_session(session_id)
        state.status = "active"
        state.input_mode = mode
        self._ensure_worker(state)
        await self.publish(
            make_event(
                EventType.AUDIO_STATUS,
                session_id,
                {"input_mode": mode, "status": "started"},
            )
        )
        return state

    async def update_caller_metadata(
        self, session_id: str, metadata: CallerMetadata
    ) -> CallState:
        state = self.require_session(session_id)
        state.caller_metadata = metadata
        state.caller_number = metadata.caller_number
        await self.publish(
            make_event(
                EventType.SYSTEM_STATUS,
                session_id,
                {"caller_metadata": metadata.model_dump(mode="json")},
            )
        )
        return state

    async def submit_transcript(self, session_id: str, payload: TranscriptIn) -> Utterance:
        state = self.require_session(session_id)
        self._ensure_worker(state)
        utterance = Utterance(session_id=session_id, **payload.model_dump())
        await self.workers[session_id].submit(utterance)
        return utterance

    async def analyze_now(self, session_id: str) -> CallState:
        state = self.require_session(session_id)
        events = await run_deep_analysis(state, self.settings)
        for event in events:
            await self.publish(event)
        return state

    async def publish(self, event: EventEnvelope) -> None:
        state = self.sessions.get(event.session_id)
        if state:
            event.sequence = state.next_sequence()
        if event.type in {EventType.SAFETY_WARNING, EventType.DECISION_UPDATE} and self.mobile_pusher:
            await self.websocket_manager.broadcast(event, kinds=("dashboard",))
            await self.mobile_pusher(event.session_id, event.payload)
            return
        await self.websocket_manager.broadcast(event)

    def snapshot(self, state: CallState) -> dict:
        return {
            "session_id": state.session_id,
            "status": state.status,
            "input_mode": state.input_mode,
            "caller_number": state.caller_number,
            "started_at": state.started_at.isoformat(),
            "ended_at": state.ended_at.isoformat() if state.ended_at else None,
            "current_risk": state.current_risk,
            "risk_level": state.current_level,
            "recent_transcript": [
                item.model_dump(mode="json") for item in state.transcript_window[-12:]
            ],
            "evidence_events": [
                item.model_dump(mode="json") for item in state.evidence_events[-20:]
            ],
            "privacy_status": {
                "raw_audio_saved": False,
                "unredacted_transcript_saved": False,
                "processing": "local",
            },
            "llm_available": state.llm_available,
        }

    async def shutdown(self) -> None:
        for session_id in list(self.workers):
            await self.stop_session_worker(session_id)
        self.sessions.clear()

    def require_session(self, session_id: str) -> CallState:
        state = self.sessions.get(session_id)
        if state is None:
            raise KeyError(session_id)
        return state

    def _ensure_worker(self, state: CallState) -> None:
        if state.session_id not in self.workers:
            self.workers[state.session_id] = SessionWorker(
                state=state,
                settings=self.settings,
                broadcaster=self.publish,
            )
        self.workers[state.session_id].start()

    async def stop_session_worker(self, session_id: str) -> None:
        worker = self.workers.pop(session_id, None)
        if worker:
            await worker.stop()
