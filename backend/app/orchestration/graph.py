import asyncio
from datetime import datetime, timezone
from typing import Any

from backend.app.config import Settings
from backend.app.orchestration.llm import deterministic_decision, try_llm_decision
from backend.app.orchestration.routing import should_trigger_deep_analysis
from backend.app.orchestration.state import CallState
from backend.app.schemas.decision import RiskSnapshot
from backend.app.schemas.evidence import EvidenceEvent
from backend.app.schemas.events import EventType, make_event
from backend.app.schemas.identity import CommunityMatch, IdentityClaim, VerificationResult
from backend.app.schemas.transcript import Utterance


LABEL_SEVERITY = {
    "SECRET_REQUEST": 5,
    "REMOTE_ACCESS": 5,
    "PAYMENT_REQUEST": 5,
    "FEAR_THREAT": 4,
    "ISOLATION": 4,
    "AUTHORITY_CLAIM": 3,
    "URGENCY": 3,
}


async def process_utterance(
    state: CallState,
    utterance: Utterance,
    settings: Settings,
) -> list[Any]:
    state.add_utterance(utterance, settings.transcript_window_seconds)
    events: list[Any] = [
        make_event(
            EventType.TRANSCRIPT_FINAL,
            state.session_id,
            utterance.model_dump(mode="json"),
        )
    ]

    evidence = run_fast_detection(utterance)
    state.evidence_events.extend(evidence)
    if evidence:
        events.append(
            make_event(
                EventType.FAST_DETECTION,
                state.session_id,
                {"utterance_id": utterance.utterance_id, "evidence": [e.model_dump(mode="json") for e in evidence]},
            )
        )
        for item in evidence:
            events.append(
                make_event(EventType.TACTIC_DETECTED, state.session_id, item.model_dump(mode="json"))
            )

    update_risk_from_evidence(state, evidence)
    if state.risk_history:
        events.append(
            make_event(
                EventType.RISK_UPDATE,
                state.session_id,
                state.risk_history[-1].model_dump(mode="json"),
            )
        )

    if should_trigger_deep_analysis(state, evidence, settings):
        deep_events = await run_deep_analysis(state, settings)
        events.extend(deep_events)

    if state.current_level in {"HIGH", "CRITICAL"}:
        events.append(
            make_event(
                EventType.SAFETY_WARNING,
                state.session_id,
                {
                    "risk": state.current_risk,
                    "level": state.current_level,
                    "message": "Do not share codes, payment details, or install remote-access apps. End the call and verify independently.",
                },
            )
        )

    return events


def run_fast_detection(utterance: Utterance) -> list[EvidenceEvent]:
    try:
        from backend.app.detection.service import detect

        result = detect(utterance.redacted_text or utterance.text)
        labels = list(getattr(result, "detected_labels", []))
        return [
            EvidenceEvent(
                utterance_id=utterance.utterance_id,
                label=label,
                description=f"Detected {label.replace('_', ' ').lower()} in the latest utterance.",
                severity=LABEL_SEVERITY.get(label, 2),
                confidence=float(getattr(result, "confidence", 1.0)),
                source="fast_detector",
            )
            for label in labels
        ]
    except Exception:
        return []


def update_risk_from_evidence(state: CallState, evidence: list[EvidenceEvent]) -> None:
    if not evidence:
        return
    added = sum(item.severity * 8 for item in evidence)
    state.current_risk = min(100, max(state.current_risk, state.current_risk + added))
    if state.current_risk >= 85:
        state.current_level = "CRITICAL"
    elif state.current_risk >= 70:
        state.current_level = "HIGH"
    elif state.current_risk >= 40:
        state.current_level = "MEDIUM"
    else:
        state.current_level = "LOW"
    state.risk_history.append(
        RiskSnapshot(
            risk=state.current_risk,
            level=state.current_level,
            reason="Updated from fast detection evidence.",
        )
    )


async def run_deep_analysis(state: CallState, settings: Settings) -> list[Any]:
    state.last_deep_analysis_at = datetime.now(timezone.utc)
    state.words_since_analysis = 0

    identity_result, community_result = await asyncio.gather(
        verify_identity(state),
        match_community(state),
        return_exceptions=True,
    )

    events: list[Any] = []
    if isinstance(identity_result, Exception):
        identity_result = VerificationResult(reason="Identity check failed without exposing internal error.")
    if isinstance(community_result, Exception):
        community_result = CommunityMatch(reason="Community lookup failed without exposing internal error.")

    state.verification_results.append(identity_result)
    state.community_matches.append(community_result)
    events.append(
        make_event(EventType.IDENTITY_VERIFIED, state.session_id, identity_result.model_dump(mode="json"))
    )
    events.append(
        make_event(EventType.COMMUNITY_MATCH, state.session_id, community_result.model_dump(mode="json"))
    )

    decision = await try_llm_decision(state, settings)
    state.llm_available = decision is not None
    if decision is None:
        decision = deterministic_decision(state)
    state.current_risk = max(state.current_risk, decision.risk)
    state.current_level = decision.level
    events.append(make_event(EventType.DECISION_UPDATE, state.session_id, decision.model_dump(mode="json")))
    events.append(make_event(EventType.RISK_UPDATE, state.session_id, decision.model_dump(mode="json")))
    return events


async def verify_identity(state: CallState) -> VerificationResult:
    recent_text = " ".join(item.text.lower() for item in state.transcript_window[-5:])
    org = None
    for candidate in ("bank", "cbi", "police", "rbi", "income tax", "customs"):
        if candidate in recent_text:
            org = candidate.upper()
            break
    if org:
        claim = IdentityClaim(organization=org)
        state.claimed_identities.append(claim)
        return VerificationResult(
            claim_id=claim.claim_id,
            status="UNVERIFIED",
            reason=f"Caller claimed {org}; trusted-directory integration pending.",
        )
    return VerificationResult(status="INSUFFICIENT_DATA", reason="No organization claim found.")


async def match_community(state: CallState) -> CommunityMatch:
    labels = {item.label for item in state.evidence_events}
    if {"AUTHORITY_CLAIM", "FEAR_THREAT", "PAYMENT_REQUEST"} & labels:
        return CommunityMatch(
            status="UNVERIFIED",
            similarity=0.62,
            pattern_name="authority_pressure_payment",
            reason="Local fallback matched a common authority-pressure scam pattern.",
        )
    return CommunityMatch()

