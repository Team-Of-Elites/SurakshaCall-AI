from datetime import datetime, timezone, timedelta
from typing import Any

from backend.app.rules.models import TemporalRuleDefinition


class TemporalMatch:
    def __init__(
        self,
        rule_id: str,
        severity: int,
        score_delta: int = 10,
        risk_floor: int | None = None,
    ):
        self.rule_id = rule_id
        self.severity = severity
        self.score_delta = score_delta
        self.risk_floor = risk_floor


def evaluate_temporal_rules(
    rules: list[TemporalRuleDefinition],
    recent_labels: list[dict[str, Any]],
    window_seconds: int = 60,
) -> list[TemporalMatch]:
    if not recent_labels:
        return []

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=window_seconds)
    recent = [r for r in recent_labels if r.get("timestamp", now) >= cutoff]
    recent_label_set = {r.get("label", "") for r in recent}

    matches: list[TemporalMatch] = []
    for rule in rules:
        if not rule.enabled:
            continue
        requires = set(rule.requires)
        if requires and requires.issubset(recent_label_set):
            matches.append(TemporalMatch(
                rule_id=rule.id,
                severity=rule.severity,
                score_delta=rule.score_delta,
                risk_floor=rule.risk_floor,
            ))
    return matches
