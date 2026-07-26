"""
SurakshaCall AI — Text Normalizer (English Only)
Owner: Lakshay
Task: L-03
Produces raw, normalized, and redacted versions of each utterance.
"""
import re
from dataclasses import dataclass
from typing import Optional


REDACT_PATTERNS = [
    (re.compile(r"\b\d{4,6}\b"), "[CODE]"),
    (re.compile(r"\b\d{10,12}\b"), "[PHONE]"),
    (re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), "[PAN]"),
    (re.compile(r"\b\d{12}\b"), "[AADHAAR]"),
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "[EMAIL]"),
]


@dataclass
class NormalizedUtterance:
    raw_text: str
    normalized_text: str
    redacted_text: str
    language: str = "en"


def normalize(raw_text: str, language: Optional[str] = None) -> NormalizedUtterance:
    """
    Normalize a raw ASR transcript utterance.
    Preserves evidence — does not remove scam indicators.
    """
    normalized = raw_text.lower().strip()

    # Build redacted version (for logging only)
    redacted = normalized
    for pattern, placeholder in REDACT_PATTERNS:
        redacted = pattern.sub(placeholder, redacted)

    return NormalizedUtterance(
        raw_text=raw_text,
        normalized_text=normalized,
        redacted_text=redacted,
        language=language or "en",
    )
