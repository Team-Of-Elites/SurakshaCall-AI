"""
SurakshaCall AI — Deterministic Rule Engine (English Only)
Owner: Lakshay
Task: L-04
Runs after every transcript utterance. Returns DetectionEvent list.
Rules ALWAYS fire regardless of classifier confidence.
"""
import re
from dataclasses import dataclass, field
from typing import List
from .labels import SEVERITY


@dataclass
class DetectionEvent:
    event_id: str
    label: str
    confidence: float
    severity: int
    source: str          # "rule" or "classifier"
    quote: str           # Exact matched phrase
    rule_id: str


# ── Pattern definitions (English Only) ──────────────────────────────────────

PATTERNS = {
    # ── SECRET_REQUEST ──────────────────────────────────────────────────────
    "secret_direct_en_01": (
        "SECRET_REQUEST",
        re.compile(r"\b(otp|one.?time.?password|pin|cvv|upi.?pin|password|passcode)\b", re.I),
    ),
    "secret_indirect_en_02": (
        "SECRET_REQUEST",
        re.compile(r"(six|6).?digit.*(code|number|message)", re.I),
    ),
    "secret_indirect_en_03": (
        "SECRET_REQUEST",
        re.compile(r"(message|sms|text).*(code|number).*(share|tell|give|read|send)", re.I),
    ),
    "secret_verification_code_en": (
        "SECRET_REQUEST",
        re.compile(r"(verification|confirmation|security)\s*(code|number).{0,30}(read|tell|share|give|send)", re.I),
    ),
    "secret_access_code_en": (
        "SECRET_REQUEST",
        re.compile(r"(give|share|tell|send|read).{0,30}(access\s*code|\d+.?digit\s*(id|code|number))", re.I),
    ),
    "secret_screen_code_en": (
        "SECRET_REQUEST",
        re.compile(r"(code|id|number)\s*(shown|displayed|on\s*(your\s*)?screen)", re.I),
    ),

    # ── PAYMENT_REQUEST ─────────────────────────────────────────────────────
    "payment_safe_account_en": (
        "PAYMENT_REQUEST",
        re.compile(r"(safe|security|verification|temporary)\s*account", re.I),
    ),
    "payment_transfer_en": (
        "PAYMENT_REQUEST",
        re.compile(r"(transfer|send|deposit).*(money|funds|amount|rupees|rs\.?|inr|lakh|crore)", re.I),
    ),
    "payment_transfer_amount_en": (
        "PAYMENT_REQUEST",
        re.compile(r"\d[\d,.]*\s*(rupees|rs\.?|inr|lakh|crore).{0,30}(transfer|send|pay|deposit)", re.I),
    ),
    "payment_transfer_reverse_en": (
        "PAYMENT_REQUEST",
        re.compile(r"(transfer|send|pay|deposit).{0,30}\d[\d,.]*\s*(rupees|rs\.?|inr|lakh|crore)", re.I),
    ),
    "payment_upi_collect": (
        "PAYMENT_REQUEST",
        re.compile(r"(approve|accept|confirm).{0,20}(upi|collect|payment).{0,20}(request|req)", re.I),
    ),
    "payment_upi_collect_reverse": (
        "PAYMENT_REQUEST",
        re.compile(r"(upi|collect).{0,20}(request|req).{0,20}(approve|accept|confirm|sent)", re.I),
    ),
    "payment_qr_scam": (
        "PAYMENT_REQUEST",
        re.compile(r"(scan|qr)\s*(code|to receive|to get|for refund)", re.I),
    ),
    "payment_scan_standalone": (
        "PAYMENT_REQUEST",
        re.compile(r"(please\s*)?scan\s*(it|this|the\s*qr)", re.I),
    ),
    "payment_release_fee": (
        "PAYMENT_REQUEST",
        re.compile(r"(release|clearance|customs|delivery)\s*(fee|charge|amount|pay)", re.I),
    ),

    # ── REMOTE_ACCESS ───────────────────────────────────────────────────────
    "remote_anydesk": (
        "REMOTE_ACCESS",
        re.compile(r"\b(anydesk|any.?desk)\b", re.I),
    ),
    "remote_teamviewer": (
        "REMOTE_ACCESS",
        re.compile(r"\b(teamviewer|team.?viewer)\b", re.I),
    ),
    "remote_quicksupport": (
        "REMOTE_ACCESS",
        re.compile(r"\b(quicksupport|quick.?support|rustdesk)\b", re.I),
    ),
    "remote_install_app": (
        "REMOTE_ACCESS",
        re.compile(r"(install|download|open)\s*(this|the|an?)\s*(app|application|software)", re.I),
    ),

    # ── ISOLATION ───────────────────────────────────────────────────────────
    "isolation_en_01": (
        "ISOLATION",
        re.compile(r"(don.?t|do not)\s*(tell|inform|contact)\s*(anyone|family|bank|police)", re.I),
    ),
    "isolation_en_02": (
        "ISOLATION",
        re.compile(r"(stay|remain)\s*on\s*(the\s*)?(line|call|phone)", re.I),
    ),
    "isolation_en_03": (
        "ISOLATION",
        re.compile(r"(don.?t|do not)\s*(disconnect|hang up|cut the call)", re.I),
    ),

    # ── AUTHORITY_CLAIM ─────────────────────────────────────────────────────
    "authority_cbi": (
        "AUTHORITY_CLAIM",
        re.compile(r"\b(cbi|central bureau of investigation)\b", re.I),
    ),
    "authority_ed": (
        "AUTHORITY_CLAIM",
        re.compile(r"\b(enforcement directorate|ed officer)\b", re.I),
    ),
    "authority_rbi": (
        "AUTHORITY_CLAIM",
        re.compile(r"\b(rbi|reserve bank of india)\b", re.I),
    ),
    "authority_cyber": (
        "AUTHORITY_CLAIM",
        re.compile(r"\b(cyber\s*crime|cybercrime\s*(department|cell|police))\b", re.I),
    ),
    "authority_trai": (
        "AUTHORITY_CLAIM",
        re.compile(r"\b(trai|telecom regulatory)\b", re.I),
    ),

    # ── FEAR_THREAT ─────────────────────────────────────────────────────────
    "fear_arrest": (
        "FEAR_THREAT",
        re.compile(r"(arrest|arrested|warrant|non.?bailable|nbw)", re.I),
    ),
    "fear_freeze": (
        "FEAR_THREAT",
        re.compile(r"(freeze|frozen|block|suspend|seize).*(account|sim|number|card)", re.I),
    ),
    "fear_freeze_reverse": (
        "FEAR_THREAT",
        re.compile(r"(account|sim|number|card).*(freeze|frozen|block|blocked|suspend|suspended|seize|seized)", re.I),
    ),
    "fear_legal": (
        "FEAR_THREAT",
        re.compile(r"(fir|legal action|court|jail|prison|section 420|case filed)", re.I),
    ),

    # ── URGENCY ─────────────────────────────────────────────────────────────
    "urgency_time_en": (
        "URGENCY",
        re.compile(r"(immediately|right now|within\s*\d+\s*(minutes?|hours?)|before\s*(end|tonight|5 pm))", re.I),
    ),

    # ── SCREEN_SHARE ────────────────────────────────────────────────────────
    "screen_share": (
        "SCREEN_SHARE",
        re.compile(r"(share\s*(your\s*)?screen|screen.?share|screen.?sharing)", re.I),
    ),
}


def run_rules(text: str, event_counter: int = 0) -> List[DetectionEvent]:
    """
    Run all deterministic rules against a single utterance.
    Returns a list of DetectionEvent objects.
    Never silences a critical rule — they always fire at confidence=0.99.
    """
    events = []
    seen_labels = set()

    for rule_id, (label, pattern) in PATTERNS.items():
        match = pattern.search(text)
        if match:
            if label in seen_labels:
                continue
            seen_labels.add(label)
            event_counter += 1
            events.append(DetectionEvent(
                event_id=f"evt_{event_counter:04d}",
                label=label,
                confidence=0.99,
                severity=SEVERITY.get(label, 1),
                source="rule",
                quote=match.group(0),
                rule_id=rule_id,
            ))

    return events
