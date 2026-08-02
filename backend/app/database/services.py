import sqlite3
from typing import List, Any
from .connection import transaction
from .repositories import EvidenceRepository, RiskRepository, SessionRepository
from ..contracts.database_models import DetectionResult, RiskDecision

def persist_decision_bundle(
    conn: sqlite3.Connection,
    evidence_events: List[DetectionResult],
    risk_decision: RiskDecision,
    metrics: List[Any]  # Placeholder for MetricRecord
) -> None:
    """
    Persists evidence events and a risk snapshot atomically in a single transaction.
    """
    evidence_repo = EvidenceRepository(conn)
    risk_repo = RiskRepository(conn)
    session_repo = SessionRepository(conn)

    with transaction(conn):
        for ev in evidence_events:
            evidence_repo.add_evidence_event(
                evidence_id=ev.evidence_id,
                session_id=ev.session_id,
                event_sequence=ev.occurred_ms, # Mocking sequence
                occurred_ms=ev.occurred_ms,
                evidence_type=ev.evidence_type,
                label_code=ev.label_code,
                severity=ev.severity,
                confidence=ev.confidence,
                source_type=ev.source_type,
                source_version=ev.source_version,
                evidence_text_redacted=ev.evidence_text_redacted,
                created_at_utc=risk_decision.occurred_ms # Mocking time
            )

        risk_repo.add_risk_snapshot(
            snapshot_id=risk_decision.snapshot_id,
            session_id=risk_decision.session_id,
            state_version=risk_decision.state_version,
            occurred_ms=risk_decision.occurred_ms,
            risk_index=risk_decision.risk_index,
            risk_band=risk_decision.risk_band,
            decision_code=risk_decision.decision_code,
            created_at_utc=str(risk_decision.occurred_ms)
        )

        session_repo.update_maximum_risk(
            session_id=risk_decision.session_id,
            risk_index=risk_decision.risk_index
        )
        
        # Metric persistence could be added here
