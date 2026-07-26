from datetime import datetime, timezone

from backend.app.config import Settings
from backend.app.orchestration.state import CallState
from backend.app.schemas.evidence import EvidenceEvent


HIGH_IMPACT_LABELS = {
    "SECRET_REQUEST",
    "PAYMENT_REQUEST",
    "REMOTE_ACCESS",
    "ISOLATION",
    "AUTHORITY_CLAIM",
}


def should_trigger_deep_analysis(
    state: CallState,
    new_evidence: list[EvidenceEvent],
    settings: Settings,
    analyze_now: bool = False,
) -> bool:
    if analyze_now:
        return True
    if any(item.severity >= 5 for item in new_evidence):
        return True
    if state.current_risk >= 25:
        return True
    if any(item.label in HIGH_IMPACT_LABELS for item in new_evidence):
        return True
    if state.words_since_analysis >= settings.minimum_new_words:
        return True
    if state.last_deep_analysis_at is None:
        return bool(new_evidence)

    now = datetime.now(timezone.utc)
    elapsed = (now - state.last_deep_analysis_at).total_seconds()
    interval = (
        settings.high_risk_interval_seconds
        if state.current_risk >= 70
        else settings.normal_interval_seconds
    )
    return elapsed >= interval and state.words_since_analysis > 0
