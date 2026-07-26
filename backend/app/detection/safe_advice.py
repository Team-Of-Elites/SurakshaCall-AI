"""
SurakshaCall AI — Safe Advice Detector (English Only)
Owner: Lakshay
Task: L-05

Prevents protective statements from being flagged as scam indicators.
Three detection layers:
  1. Negation patterns: "never share your OTP", "don't give your PIN"
  2. Question patterns: "did you receive an OTP?" (not a demand)
  3. Reporting patterns: "report to cybercrime" context
"""
import re
from typing import List

# ── Layer 1: Negation / protective warnings ─────────────────────────────────
SAFE_NEGATION_PATTERNS = [
    # "never share your OTP", "don't give your PIN"
    re.compile(r"(never|don.?t|do not|never ever).{0,30}(share|give|tell|disclose).{0,30}(otp|pin|cvv|password|code|credential)", re.I),
    # Reverse: "OTP should never be shared"
    re.compile(r"(otp|pin|cvv|password|code|credential).{0,30}(never|don.?t|do not|never ever).{0,20}(share|give|tell|disclose)", re.I),
    # "bank never asks" / "staff will never ask" / "will ever ask"
    re.compile(r"(bank|staff|officer|employee|we).{0,40}(never|never asks?|won.?t|will not|does not|will ever).{0,20}(ask|request|demand)", re.I),
    # "protect/keep your OTP"
    re.compile(r"(protect|keep|save|guard).{0,20}(your\s*)?(otp|pin|password|code|cvv)", re.I),
    # "legitimate/real org never asks"
    re.compile(r"(legitimate|real|official|genuine).{0,30}(never|won.?t|will not|does not).{0,20}(ask|request)", re.I),
    # "be careful with your OTP"
    re.compile(r"(be\s*careful|beware|stay\s*alert|be\s*aware|caution).{0,40}(otp|pin|cvv|password|code|credential)", re.I),
]

# ── Layer 2: Question-form / non-demand mentions ────────────────────────────
SAFE_QUESTION_PATTERNS = [
    # "did you receive an OTP" — inquiry, not demand
    re.compile(r"(did\s*you|have\s*you).{0,20}(receive|get).{0,15}(otp|code|pin|message)", re.I),
    # "if anyone asks for your PIN" — hypothetical warning
    re.compile(r"(if\s*(any|some)one).{0,30}(asks?|request).{0,15}(otp|pin|cvv|password|code)", re.I),
    # "no need to share"
    re.compile(r"no\s*need\s*to\s*(share|give|tell|send)", re.I),
]

# ── Layer 3: Reporting / cybercrime context ──────────────────────────────────
SAFE_REPORTING_PATTERNS = [
    # "report to cybercrime" / "call 1930"
    re.compile(r"(report|call|contact|visit).{0,20}(cybercrime|cyber\s*crime|1930|police|helpline)", re.I),
    # "hang up and report"
    re.compile(r"(hang\s*up|disconnect).{0,20}(report|complain)", re.I),
]


def is_safe_advice(text: str) -> bool:
    """
    Returns True if the utterance is protective/advisory in nature.
    Checks all three layers — any match means safe advice.
    """
    for pattern in SAFE_NEGATION_PATTERNS:
        if pattern.search(text):
            return True
    for pattern in SAFE_QUESTION_PATTERNS:
        if pattern.search(text):
            return True
    for pattern in SAFE_REPORTING_PATTERNS:
        if pattern.search(text):
            return True
    return False


def filter_safe_advice(text: str, detected_labels: List[str]) -> List[str]:
    """
    If text is safe advice, remove ALL conflicting critical labels.
    A genuine protective statement should never trigger a critical alert.
    """
    if is_safe_advice(text):
        critical_to_remove = {"SECRET_REQUEST", "PAYMENT_REQUEST", "REMOTE_ACCESS"}
        filtered = [
            label for label in detected_labels
            if label not in critical_to_remove
        ]
        if "SAFE_ADVICE" not in filtered:
            filtered.append("SAFE_ADVICE")
        return filtered
    return detected_labels
