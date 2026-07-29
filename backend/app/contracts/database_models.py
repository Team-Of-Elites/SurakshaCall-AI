from typing import Literal, Dict, Any, List, Optional
from pydantic import BaseModel, Field

PrivacyMode = Literal["MAXIMUM_PRIVACY", "EVALUATION"]
InputMode = Literal["MICROPHONE", "REPLAY", "MOCK"]

class TranscriptFinal(BaseModel):
    event_id: str
    session_id: str
    utterance_id: str
    sequence: int
    speaker: Literal["CALLER", "USER", "UNKNOWN"]
    started_ms: int = Field(ge=0)
    ended_ms: int = Field(ge=0)
    raw_text: str
    language_code: Optional[str] = None
    asr_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    asr_model_id: str
    occurred_at_utc: str

class DetectionResult(BaseModel):
    evidence_id: str
    session_id: str
    occurred_ms: int = Field(ge=0)
    evidence_type: str
    label_code: str
    severity: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0, le=1)
    score_delta: float
    risk_floor: Optional[float] = Field(default=None, ge=0, le=100)
    source_type: Literal["RULE", "ML", "LLM", "IDENTITY", "COMMUNITY", "SYSTEM"]
    source_version: str
    supporting_utterance_ids: List[str]
    evidence_text_redacted: Optional[str] = None
    metadata: Dict[str, Any]

class RiskDecision(BaseModel):
    snapshot_id: str
    session_id: str
    state_version: int
    occurred_ms: int
    risk_index: float = Field(ge=0, le=100)
    risk_band: Literal["LOW", "CAUTION", "HIGH", "CRITICAL"]
    decision_code: str
    hard_floor: float = Field(ge=0, le=100)
    reason_codes: List[str]
    evidence_ids: List[str]
    component_scores: Dict[str, float]
    headline_code: Optional[str] = None

class DatabaseHealthEvent(BaseModel):
    event: Literal["database_health"]
    session_id: Optional[str]
    status: Literal["AVAILABLE", "DEGRADED", "UNAVAILABLE", "RECOVERED"]
    persistence_enabled: bool
    safe_fallback_active: bool
    error_code: Optional[str]
    occurred_at_utc: str
