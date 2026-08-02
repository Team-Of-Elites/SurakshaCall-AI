import asyncio
import json
from typing import Any

from backend.app.config import Settings
from backend.app.orchestration.state import CallState
from backend.app.risk.decision import build_decision, build_decision_from_llm
from backend.app.schemas.decision import RiskDecision

SYSTEM_PROMPT = """
You are SurakshaCall AI's local risk decision helper.
Return only compact JSON with keys: risk, level, action, explanation.
Never ask for secrets. Never reduce deterministic critical risk.
""".strip()


def build_decision_context(state: CallState) -> dict[str, Any]:
    return {
        "session_id": state.session_id,
        "current_risk": state.current_risk,
        "current_level": state.current_level,
        "recent_transcript": [
            {
                "text": item.redacted_text or item.text,
                "speaker": item.speaker,
                "language": item.language,
            }
            for item in state.transcript_window[-6:]
        ],
        "evidence": [
            {
                "label": item.label,
                "severity": item.severity,
                "confidence": item.confidence,
                "description": item.description,
            }
            for item in state.evidence_events[-10:]
        ],
        "identity": [item.model_dump(mode="json") for item in state.verification_results[-3:]],
        "community": [item.model_dump(mode="json") for item in state.community_matches[-3:]],
    }


async def try_llm_decision(state: CallState, settings: Settings) -> RiskDecision | None:
    if not getattr(settings, "local_llm_enabled", False):
        return None
    if not _ollama_server_available():
        return None
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_ollama_decision_sync, state, settings),
            timeout=min(settings.llm_timeout_seconds, 2.0),
        )
    except Exception:
        return None


def _ollama_server_available() -> bool:
    try:
        import urllib.request

        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=0.25) as response:
            return 200 <= response.status < 500
    except Exception:
        return False


def _ollama_decision_sync(state: CallState, settings: Settings) -> RiskDecision | None:
    try:
        import ollama
    except Exception:
        return None

    context = build_decision_context(state)
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context JSON:\n{json.dumps(context, ensure_ascii=False)}\n\n"
        "Return JSON only."
    )
    try:
        response = ollama.chat(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1, "num_predict": 180},
        )
        content = response.get("message", {}).get("content", "")
        parsed = _extract_json(content)
        if not parsed:
            return None
        return build_decision_from_llm(state, parsed)
    except Exception:
        return None


def _extract_json(content: str) -> dict[str, Any] | None:
    content = content.strip()
    if not content:
        return None
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        data = json.loads(content[start : end + 1])
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def deterministic_decision(state: CallState) -> RiskDecision:
    return build_decision(state)
