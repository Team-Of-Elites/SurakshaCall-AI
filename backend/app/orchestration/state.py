from datetime import datetime, timedelta, timezone
from typing import Literal

from pydantic import BaseModel, Field

from backend.app.schemas.decision import RiskLevel, RiskSnapshot
from backend.app.schemas.evidence import EvidenceEvent
from backend.app.schemas.identity import (
    CommunityMatch,
    IdentityClaim,
    VerificationResult,
)
from backend.app.schemas.transcript import Utterance


InputMode = Literal["idle", "microphone", "replay"]
SessionStatus = Literal["created", "active", "ended"]


class CallerMetadata(BaseModel):
    caller_number: str | None = None
    direction: Literal["incoming", "outgoing", "unknown"] = "unknown"
    display_name: str | None = None
    notes: str | None = None


class CallState(BaseModel):
    session_id: str
    caller_number: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime | None = None
    status: SessionStatus = "created"
    input_mode: InputMode = "idle"
    transcript_window: list[Utterance] = Field(default_factory=list)
    previous_summary: str = ""
    evidence_events: list[EvidenceEvent] = Field(default_factory=list)
    claimed_identities: list[IdentityClaim] = Field(default_factory=list)
    verification_results: list[VerificationResult] = Field(default_factory=list)
    community_matches: list[CommunityMatch] = Field(default_factory=list)
    current_risk: int = 0
    current_level: RiskLevel = "LOW"
    risk_history: list[RiskSnapshot] = Field(default_factory=list)
    last_deep_analysis_at: datetime | None = None
    words_since_analysis: int = 0
    llm_available: bool = True
    caller_metadata: CallerMetadata = Field(default_factory=CallerMetadata)
    sequence: int = 0

    def next_sequence(self) -> int:
        self.sequence += 1
        return self.sequence

    def add_utterance(self, utterance: Utterance, window_seconds: int) -> None:
        self.transcript_window.append(utterance)
        self.words_since_analysis += len(utterance.text.split())
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
        retained: list[Utterance] = []
        summarized: list[str] = []
        for item in self.transcript_window:
            if item.created_at >= cutoff:
                retained.append(item)
            elif not any(ev.utterance_id == item.utterance_id for ev in self.evidence_events):
                summarized.append(item.redacted_text or item.text)
            else:
                retained.append(item)
        if summarized:
            joined = " ".join(summarized)
            self.previous_summary = f"{self.previous_summary} {joined}".strip()[-1200:]
        self.transcript_window = retained

    def reset_for_demo(self) -> None:
        self.ended_at = None
        self.status = "created"
        self.input_mode = "idle"
        self.transcript_window.clear()
        self.previous_summary = ""
        self.evidence_events.clear()
        self.claimed_identities.clear()
        self.verification_results.clear()
        self.community_matches.clear()
        self.current_risk = 0
        self.current_level = "LOW"
        self.risk_history.clear()
        self.last_deep_analysis_at = None
        self.words_since_analysis = 0
