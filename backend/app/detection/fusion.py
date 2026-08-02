from backend.app.detection.schemas import DetectionEvent, LabelScore
from backend.app.rules.engine import RuleMatch


def combine_events(
    rule_matches: list[RuleMatch],
    label_scores: list[LabelScore] | None = None,
    safe_advice_labels: set[str] | None = None,
) -> list[DetectionEvent]:
    safe_advice_labels = safe_advice_labels or set()
    seen_labels: set[str] = set()
    events: list[DetectionEvent] = []

    for rule in rule_matches:
        if rule.label in seen_labels:
            continue
        if rule.label in safe_advice_labels and rule.label != "SAFE_ADVICE":
            continue
        seen_labels.add(rule.label)
        events.append(DetectionEvent(
            event_id=f"evt_{len(events):04d}",
            label=rule.label,
            confidence=rule.confidence,
            severity=rule.severity,
            source="rule",
            rule_id=rule.rule_id,
            evidence_quotes=[rule.evidence_quote],
            score_delta=rule.score_delta,
            risk_floor=rule.risk_floor,
            recommended_action_code=rule.action_code or None,
        ))

    if label_scores:
        for score in label_scores:
            if score.emitted and score.label not in seen_labels:
                seen_labels.add(score.label)
                events.append(DetectionEvent(
                    event_id=f"evt_{len(events):04d}",
                    label=score.label,
                    confidence=score.calibrated_score or score.raw_score,
                    severity=_label_severity(score.label),
                    source="classifier",
                    uncertainty="low" if score.emitted else "medium",
                ))

    return events


def _label_severity(label: str) -> int:
    severity_map = {
        "SECRET_REQUEST": 5,
        "REMOTE_ACCESS": 5,
        "PAYMENT_REQUEST": 5,
        "FEAR_THREAT": 4,
        "ISOLATION": 4,
        "AUTHORITY_CLAIM": 3,
        "URGENCY": 3,
        "SCREEN_SHARE": 3,
        "CHANNEL_SWITCH": 2,
        "REWARD_SCARCITY": 2,
        "PERSISTENCE": 2,
        "SAFE_ADVICE": 0,
        "NORMAL_SERVICE": 0,
    }
    return severity_map.get(label, 2)
