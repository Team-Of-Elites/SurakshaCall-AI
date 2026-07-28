from backend.app.config import Settings
from backend.app.orchestration.llm import build_decision_context, try_llm_decision
from backend.app.orchestration.state import CallState
from backend.app.schemas.decision import RiskDecision


async def analyze_context(
    state: CallState,
    settings: Settings,
) -> RiskDecision | None:
    decision = await try_llm_decision(state, settings)
    return decision
