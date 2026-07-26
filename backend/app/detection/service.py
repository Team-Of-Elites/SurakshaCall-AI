import re

from pydantic import BaseModel, Field


class DetectionResult(BaseModel):
    detected_labels: list[str] = Field(default_factory=list)
    is_critical: bool = False
    safe_advice_detected: bool = False
    confidence: float = 1.0


SAFE_ADVICE_PATTERNS = [
    re.compile(r"\bnever\s+share\b.*\b(otp|pin|cvv|code)\b", re.IGNORECASE),
    re.compile(r"\b(real\s+)?bank\b.*\bnever\s+ask", re.IGNORECASE),
]

RULES: list[tuple[str, re.Pattern[str]]] = [
    ("SECRET_REQUEST", re.compile(r"\b(share|tell|bataiye|bolo|batana|do)\b.*\b(otp|code|pin|cvv|six digit|6 digit|chhe ank)\b|\b(otp|code|pin|cvv|six digit|6 digit|chhe ank)\b.*\b(share|tell|bataiye|bolo|batana)\b", re.IGNORECASE)),
    ("REMOTE_ACCESS", re.compile(r"\b(anydesk|teamviewer|remote access|screen share|install.*app)\b", re.IGNORECASE)),
    ("PAYMENT_REQUEST", re.compile(r"\b(upi collect|approve.*upi|transfer.*amount|safe account|send money|pay now)\b", re.IGNORECASE)),
    ("ISOLATION", re.compile(r"\b(kisi ko mat batana|do not tell|don't tell|confidential|classified)\b", re.IGNORECASE)),
    ("AUTHORITY_CLAIM", re.compile(r"\b(cbi|police|rbi|income tax|customs|officer|inspector)\b", re.IGNORECASE)),
    ("FEAR_THREAT", re.compile(r"\b(arrest|warrant|non-bailable|jail|case.*filed|blocked forever)\b", re.IGNORECASE)),
    ("URGENCY", re.compile(r"\b(10 minutes|within \d+ minutes|abhi|right now|immediately|urgent)\b", re.IGNORECASE)),
]

CRITICAL_LABELS = {"SECRET_REQUEST", "REMOTE_ACCESS", "PAYMENT_REQUEST"}


def detect(text: str) -> DetectionResult:
    safe_advice = any(pattern.search(text) for pattern in SAFE_ADVICE_PATTERNS)
    labels: list[str] = []
    if not safe_advice:
        for label, pattern in RULES:
            if pattern.search(text):
                labels.append(label)
    return DetectionResult(
        detected_labels=labels,
        is_critical=any(label in CRITICAL_LABELS for label in labels),
        safe_advice_detected=safe_advice,
    )
