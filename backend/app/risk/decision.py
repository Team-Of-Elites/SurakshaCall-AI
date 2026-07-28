from backend.app.orchestration.state import CallState
from backend.app.risk.explainer import default_action, default_explanation
from backend.app.risk.scorer import RiskLevel, _level_for_risk
from backend.app.schemas.decision import RiskDecision


def build_decision(state: CallState) -> RiskDecision:
    risk = int(state.current_risk)
    level = state.current_level
    return RiskDecision(
        session_id=state.session_id,
        risk=risk,
        level=level,
        action=default_action(level),
        explanation=default_explanation(level),
        evidence_ids=[item.evidence_id for item in state.evidence_events[-8:]],
    )


def build_decision_from_llm(state: CallState, llm_payload: dict) -> RiskDecision:
    deterministic_risk = int(state.current_risk)
    risk = _safe_int(llm_payload.get("risk"), deterministic_risk)
    risk = max(deterministic_risk, min(100, max(0, risk)))
    level = str(llm_payload.get("level") or _level_for_risk(risk)).upper()
    if level not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        level = _level_for_risk(risk)
    deterministic_level = _level_for_risk(deterministic_risk)
    if _level_rank(level) < _level_rank(deterministic_level):
        level = deterministic_level
    action = str(llm_payload.get("action") or default_action(level))[:300]
    explanation = str(llm_payload.get("explanation") or default_explanation(level))[:500]
    return RiskDecision(
        session_id=state.session_id,
        risk=risk,
        level=level,
        action=action,
        explanation=explanation,
        evidence_ids=[item.evidence_id for item in state.evidence_events[-8:]],
    )


def _safe_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _level_rank(level: str) -> int:
    return {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}.get(level, 0)
