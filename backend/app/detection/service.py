"""
SurakshaCall AI — Detection Service
Owner: Lakshay
Task: L-07

THIS IS THE TEAM API CONTRACT.
All other modules consume the output of detect() from this file.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from pydantic import BaseModel, Field

from .rules import run_rules, DetectionEvent
from .normalizer import normalize, NormalizedUtterance
from .safe_advice import filter_safe_advice
from .labels import CRITICAL_LABELS, SEVERITY


class DetectionResult(BaseModel):
    """Output schema — agreed across team modules."""
    utterance_normalized: str = ""
    utterance_redacted: str = ""
    language: str = "en"
    events: List[dict] = Field(default_factory=list)
    detected_labels: List[str] = Field(default_factory=list)
    is_critical: bool = False            # True if any CRITICAL_LABELS detected
    max_severity: int = 0                # 0–5
    trigger_llm: bool = False            # Whether this result should invoke the LLM
    safe_advice_detected: bool = False
    confidence: float = 1.0


def detect(raw_text: str, language: Optional[str] = None) -> DetectionResult:
    """
    Main entry point.
    Run normalization → rules → safe-advice filter → build result.
    """
    norm = normalize(raw_text, language)

    # Run deterministic rules
    rule_events = run_rules(norm.normalized_text)

    # Extract labels from rule events
    detected_labels = list({e.label for e in rule_events})

    # Safe advice filter — prevents false positives
    safe_advice = False
    if detected_labels or norm.normalized_text:
        filtered = filter_safe_advice(norm.normalized_text, detected_labels)
        if filtered != detected_labels:
            safe_advice = True
            detected_labels = filtered
            rule_events = [e for e in rule_events if e.label in detected_labels]

    is_critical = bool(CRITICAL_LABELS & set(detected_labels))
    max_severity = max((SEVERITY.get(lbl, 0) for lbl in detected_labels), default=0)

    # Trigger LLM if critical, or if 2+ labels detected
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
        utterance_normalized=norm.normalized_text,
        utterance_redacted=norm.redacted_text,
        language=norm.language,
        events=events_dict,
        detected_labels=detected_labels,
        is_critical=is_critical,
        max_severity=max_severity,
        trigger_llm=trigger_llm,
        safe_advice_detected=safe_advice,
        confidence=0.99 if rule_events else 1.0,
    )
