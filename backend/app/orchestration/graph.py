import asyncio
from datetime import datetime, timezone
from typing import Any

from backend.app.config import Settings
from backend.app.orchestration.llm import deterministic_decision, try_llm_decision
from backend.app.orchestration.routing import should_trigger_deep_analysis
from backend.app.orchestration.state import CallState
from backend.app.risk.scorer import compute_risk_from_evidence
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
    broadcaster: Any = None,
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

    if broadcaster:
        for event in events:
            await broadcaster(event)

    if should_trigger_deep_analysis(state, evidence, settings):
        if broadcaster:
            asyncio.create_task(_run_deep_and_broadcast(state, settings, broadcaster))
        else:
            deep_events = await run_deep_analysis(state, settings)
            events.extend(deep_events)

    return events


async def _run_deep_and_broadcast(state: CallState, settings: Settings, broadcaster: Any) -> None:
    try:
        deep_events = await run_deep_analysis(state, settings)
        for event in deep_events:
            await broadcaster(event)
    except Exception as exc:
        print(f"GRAPH: deep analysis error: {exc}", flush=True)


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
    severities = [item.severity for item in evidence]
    update = compute_risk_from_evidence(state.current_risk, severities)
    state.current_risk = update.risk
    state.current_level = update.level
    state.risk_history.append(
        RiskSnapshot(
            risk=update.risk,
            level=update.level,
            reason=update.reason,
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

    if identity_result.risk_contribution > 0:
        from backend.app.risk.scorer import merge_identity_risk
        id_update = merge_identity_risk(state.current_risk, identity_result.risk_contribution)
        state.current_risk = id_update.risk
        state.current_level = id_update.level

    if community_result.similarity > 0:
        from backend.app.risk.scorer import merge_community_risk
        cm_update = merge_community_risk(state.current_risk, community_result.similarity)
        state.current_risk = cm_update.risk
        state.current_level = cm_update.level

    decision = await try_llm_decision(state, settings)
    state.llm_available = decision is not None
    if decision is None:
        from backend.app.risk.decision import build_decision
        decision = build_decision(state)
    state.current_risk = max(state.current_risk, decision.risk)
    state.current_level = decision.level
    events.append(make_event(EventType.DECISION_UPDATE, state.session_id, decision.model_dump(mode="json")))
    events.append(make_event(EventType.RISK_UPDATE, state.session_id, decision.model_dump(mode="json")))
    return events


async def verify_identity(state: CallState) -> VerificationResult:
    try:
        from backend.app.database.connection import get_connection
        from backend.app.identity.verifier import verify_identity as real_verify

        recent_text = " ".join(item.text.lower() for item in state.transcript_window[-5:])
        claimed_org = None
        for candidate in ("sbi", "state bank", "cbi", "police", "rbi", "income tax", "customs", "hdfc", "icici"):
            if candidate in recent_text:
                claimed_org = candidate.upper()
                break

        detected_labels = list({e.label for e in state.evidence_events})
        caller_number = state.caller_number

        result = real_verify(
            phone_number=caller_number,
            claimed_org_name=claimed_org,
            detected_labels=detected_labels,
        )

        if result.claimed_org:
            claim = IdentityClaim(organization=result.canonical_org or result.claimed_org)
            state.claimed_identities.append(claim)
            return VerificationResult(
                claim_id=claim.claim_id,
                status=_map_identity_status(result.status),
                reason=result.explanation,
                risk_contribution=result.risk_contribution,
            )

        return VerificationResult(
            status="INSUFFICIENT_DATA",
            reason="No organization claim found.",
            risk_contribution=0,
        )
    except Exception as exc:
        return VerificationResult(
            status="INSUFFICIENT_DATA",
            reason=f"Identity verification unavailable: {exc}",
            risk_contribution=5,
        )


async def match_community(state: CallState) -> CommunityMatch:
    try:
        from backend.app.database.connection import get_connection
        from backend.app.community.service import evaluate_community_risk
        from backend.app.community.fingerprint import CommunityFingerprint

        conn = get_connection()
        tactics = list({e.label for e in state.evidence_events})
        if not tactics:
            return CommunityMatch(status="INSUFFICIENT_DATA", similarity=0.0, reason="No tactics to match.")

        fingerprint = CommunityFingerprint(
            tactics=tactics,
            organization_type=_guess_org_type(state),
            scenario=_guess_scenario(tactics),
            requested_action=_guess_requested_action(tactics),
            threat_type=_guess_threat_type(tactics),
            channel_switch="NONE",
            language_family="HI_EN",
        )

        match = evaluate_community_risk(conn, fingerprint.model_dump())
        conn.close()

        if match and match.get("similarity", 0) >= 0.5:
            return CommunityMatch(
                status="UNVERIFIED",
                similarity=match["similarity"],
                pattern_name=match.get("campaign_label", "unknown"),
                reason=match.get("campaign_label", "Community pattern matched."),
            )
        return CommunityMatch(
            status="INSUFFICIENT_DATA",
            similarity=0.0,
            reason="No strong community pattern match found.",
        )
    except Exception as exc:
        return CommunityMatch(
            status="INSUFFICIENT_DATA",
            similarity=0.0,
            reason=f"Community lookup unavailable: {exc}",
        )


def _map_identity_status(status: str) -> str:
    mapping = {
        "VERIFIED_OFFICIAL_NUMBER": "VERIFIED",
        "CLAIM_CONTRADICTS_POLICY": "CONTRADICTORY",
        "UNVERIFIED_NUMBER": "UNVERIFIED",
        "KNOWN_REPORTED_TEST_RISK": "UNVERIFIED",
        "ORGANIZATION_NOT_IN_DIRECTORY": "UNVERIFIED",
        "INSUFFICIENT_DATA": "INSUFFICIENT_DATA",
    }
    return mapping.get(status, "INSUFFICIENT_DATA")


def _guess_org_type(state: CallState) -> str:
    for claim in state.claimed_identities:
        org = (claim.organization or "").lower()
        if "bank" in org:
            return "BANK"
        if "cbi" in org or "police" in org or "enforcement" in org:
            return "LAW_ENFORCEMENT"
        if "rbi" in org or "trai" in org:
            return "REGULATOR"
    return "UNKNOWN"


def _guess_scenario(tactics: list[str]) -> str:
    tactics_set = set(tactics)
    if "AUTHORITY_CLAIM" in tactics_set and "FEAR_THREAT" in tactics_set:
        return "DIGITAL_ARREST"
    if "SECRET_REQUEST" in tactics_set:
        return "BANK_KYC"
    if "PAYMENT_REQUEST" in tactics_set:
        return "UPI_REFUND"
    if "REMOTE_ACCESS" in tactics_set:
        return "REMOTE_SUPPORT"
    return "AMBIGUOUS"


def _guess_requested_action(tactics: list[str]) -> str:
    tactics_set = set(tactics)
    if "SECRET_REQUEST" in tactics_set:
        return "SECRET_CODE"
    if "PAYMENT_REQUEST" in tactics_set:
        return "MONEY_TRANSFER"
    if "REMOTE_ACCESS" in tactics_set:
        return "APP_INSTALL"
    return "NONE"


def _guess_threat_type(tactics: list[str]) -> str:
    tactics_set = set(tactics)
    if "FEAR_THREAT" in tactics_set:
        return "ACCOUNT_FREEZE"
    if "ISOLATION" in tactics_set:
        return "ISOLATION"
    return "LOSS_OF_FUNDS"
