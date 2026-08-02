from typing import Any, Literal

from pydantic import BaseModel, Field


class TranscriptFinal(BaseModel):
    utterance_id: str
    session_id: str
    sequence: int = Field(ge=0)
    text: str
    language: Literal["en", "hi", "hi-en", "unknown"] = "unknown"
    speaker: Literal["caller", "user", "unknown"] = "unknown"
    started_ms: int = Field(default=0, ge=0)
    ended_ms: int = Field(default=0, ge=0)
    asr_quality: float = Field(default=1.0, ge=0, le=1)
    input_mode: Literal["microphone", "replay"] = "replay"


class DetectionEvent(BaseModel):
    event_id: str
    session_id: str = ""
    utterance_ids: list[str] = Field(default_factory=list)
    label: str
    confidence: float = Field(ge=0, le=1)
    severity: int = Field(ge=0, le=5)
    source: Literal["rule", "classifier", "rule_and_classifier"] = "rule"
    rule_id: str | None = None
    model_id: str | None = None
    evidence_quotes: list[str] = Field(default_factory=list)
    score_delta: int = 0
    risk_floor: int | None = Field(default=None, ge=0, le=100)
    recommended_action_code: str | None = None
    transcript_quality: float = Field(default=1.0, ge=0, le=1)
    uncertainty: Literal["low", "medium", "high"] = "low"


class LabelScore(BaseModel):
    label: str
    raw_score: float = 0.0
    calibrated_score: float | None = None
    threshold: float = 0.5
    emitted: bool = False


class DetectorError(BaseModel):
    code: Literal[
        "INVALID_TRANSCRIPT",
        "RULES_UNAVAILABLE",
        "MODEL_UNAVAILABLE",
        "MODEL_ARTIFACT_MISMATCH",
        "IDENTITY_DATA_UNAVAILABLE",
        "INTERNAL_ERROR",
    ]
    recoverable: bool = True
    user_safe_message: str = "An error occurred during analysis."


class DetectionResult(BaseModel):
    utterance_normalized: str = ""
    utterance_redacted: str = ""
    language: str = "en"
    events: list[dict] = Field(default_factory=list)
    detected_labels: list[str] = Field(default_factory=list)
    is_critical: bool = False
    max_severity: int = 0
    trigger_llm: bool = False
    safe_advice_detected: bool = False
    confidence: float = 1.0
