"""
SurakshaCall AI — Detection Service
Owner: Lakshay
Task: L-07

THIS IS THE TEAM API CONTRACT.
All other modules consume the output of detect() from this file.
"""
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from backend.app.detection.labels import CRITICAL_LABELS, SEVERITY
from backend.app.detection.rules import run_rules
from backend.app.detection.safe_advice import filter_safe_advice
from backend.app.language.normalizer import normalize as language_normalize
from backend.app.rules.engine import evaluate_rules
from backend.app.rules.loader import load_rules_from_yaml
from backend.app.rules.temporal import evaluate_temporal_rules


class DetectionResult(BaseModel):
    """Output schema — agreed across team modules."""
    utterance_normalized: str = ""
    utterance_redacted: str = ""
    language: str = "en"
    events: list[dict] = Field(default_factory=list)
    detected_labels: list[str] = Field(default_factory=list)
    is_critical: bool = False
    max_severity: int = 0
    trigger_llm: bool = False
    safe_advice_detected: bool = False
    confidence: float = 1.0


_RULES_CACHE: list | None = None


def _get_yaml_rules():
    global _RULES_CACHE
    if _RULES_CACHE is None:
        rules_dir = Path(__file__).parent.parent.parent.parent / "data" / "rules"
        if rules_dir.exists():
            _RULES_CACHE = load_rules_from_yaml(rules_dir)
        else:
            _RULES_CACHE = []
    return _RULES_CACHE


def detect(raw_text: str, language: Optional[str] = None) -> DetectionResult:
    norm = language_normalize(raw_text, language)
    normalized_text = norm.normalized_text

    rule_events = run_rules(normalized_text)

    yaml_rules = _get_yaml_rules()
    if yaml_rules:
        yaml_matches = evaluate_rules(norm, yaml_rules)
        for match in yaml_matches:
            if not any(e.label == match.label for e in rule_events):
                from backend.app.detection.rules import DetectionEvent as DE
                rule_events.append(DE(
                    event_id=f"evt_yaml_{len(rule_events):04d}",
                    label=match.label,
                    confidence=match.confidence,
                    severity=match.severity,
                    source="rule",
                    quote=match.evidence_quote,
                    rule_id=match.rule_id,
                ))

    detected_labels = list({e.label for e in rule_events})

    safe_advice = False
    if detected_labels or normalized_text:
        filtered = filter_safe_advice(normalized_text, detected_labels)
        if filtered != detected_labels:
            safe_advice = True
            detected_labels = filtered
            rule_events = [e for e in rule_events if e.label in detected_labels]

    is_critical = bool(CRITICAL_LABELS & set(detected_labels))
    max_severity = max((SEVERITY.get(lbl, 0) for lbl in detected_labels), default=0)
    trigger_llm = is_critical or len(detected_labels) >= 2

    events_dict = [
        {
            "event_id": e.event_id,
            "label": e.label,
            "confidence": e.confidence,
            "severity": e.severity,
            "source": e.source,
            "quote": e.quote,
            "rule_id": e.rule_id,
        }
        for e in rule_events
    ]

    return DetectionResult(
        utterance_normalized=normalized_text,
        utterance_redacted=norm.redacted_text,
        language=norm.language_mode if hasattr(norm, 'language_mode') else (language or "en"),
        events=events_dict,
        detected_labels=detected_labels,
        is_critical=is_critical,
        max_severity=max_severity,
        trigger_llm=trigger_llm,
        safe_advice_detected=safe_advice,
        confidence=0.99 if rule_events else 1.0,
    )
