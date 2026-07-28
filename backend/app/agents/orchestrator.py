from typing import Any

from backend.app.config import Settings
from backend.app.orchestration.graph import process_utterance
from backend.app.orchestration.state import CallState
from backend.app.schemas.transcript import Utterance


async def run_orchestrator(
    state: CallState,
    utterance: Utterance,
    settings: Settings,
) -> list[Any]:
    return await process_utterance(state, utterance, settings)
