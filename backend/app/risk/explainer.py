from datetime import datetime, timezone

from backend.app.schemas.decision import RiskSnapshot
from backend.app.schemas.evidence import EvidenceEvent
from backend.app.schemas.identity import CommunityMatch, VerificationResult
from backend.app.schemas.transcript import Utterance


def build_evidence_timeline(
    evidence_events: list[EvidenceEvent],
    transcript_window: list[Utterance],
    verification_results: list[VerificationResult],
    community_matches: list[CommunityMatch],
    risk_history: list[RiskSnapshot],
) -> dict:
    return {
        "evidence": [
            {
                "label": e.label,
                "severity": e.severity,
                "description": e.description,
                "source": e.source,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in evidence_events[-20:]
        ],
        "recent_transcript": [
            {
                "text": u.redacted_text or u.text,
                "speaker": u.speaker,
                "language": u.language,
            }
            for u in transcript_window[-12:]
        ],
        "identity_verifications": [
            {
                "status": v.status,
                "reason": v.reason,
                "checked_at": v.checked_at.isoformat() if v.checked_at else None,
            }
            for v in verification_results[-5:]
        ],
        "community_matches": [
            {
                "pattern": m.pattern_name,
                "similarity": m.similarity,
                "status": m.status,
            }
            for m in community_matches[-5:]
        ],
        "risk_progression": [
            {
                "risk": r.risk,
                "level": r.level,
                "reason": r.reason,
                "timestamp": r.created_at.isoformat() if r.created_at else None,
            }
            for r in risk_history[-20:]
        ],
    }


def default_explanation(level: str) -> str:
    if level == "CRITICAL":
        return "Critical scam indicators were detected in the conversation."
    if level == "HIGH":
        return "Multiple risky tactics were detected."
    if level == "MEDIUM":
        return "Some suspicious signals were detected, but more context may be needed."
    return "No high-risk pattern confirmed yet."


def default_action(level: str) -> str:
    if level == "CRITICAL":
        return "End the call and verify through an official number."
    if level == "HIGH":
        return "Do not share sensitive information; verify independently."
    if level == "MEDIUM":
        return "Pause and verify the caller before continuing."
    return "Continue monitoring."
