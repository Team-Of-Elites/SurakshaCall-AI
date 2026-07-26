"""
SurakshaCall AI — Label Taxonomy
Owner: Lakshay
Task: L-01
All utterance and scenario labels used across the detection pipeline.
"""

# ── Utterance-level labels ──────────────────────────────────────────────────
# Applied to individual turns / sentences in the conversation.

UTTERANCE_LABELS = [
    "AUTHORITY_CLAIM",   # Caller claims to be from bank, police, CBI, RBI, TRAI, etc.
    "URGENCY",           # Time-bound pressure — "10 minutes", "right now"
    "FEAR_THREAT",       # Threats of arrest, account freeze, SIM block, legal action
    "ISOLATION",         # "Don't tell anyone", "stay on call"
    "SECRET_REQUEST",    # OTP, PIN, CVV, password, 6-digit code requests
    "PAYMENT_REQUEST",   # Transfer to safe account, UPI collect, QR scan, release fee
    "REMOTE_ACCESS",     # AnyDesk, TeamViewer, QuickSupport, RustDesk install
    "SCREEN_SHARE",      # Request to share screen
    "CHANNEL_SWITCH",    # Move to WhatsApp, Telegram, video call, unknown URL
    "REWARD_SCARCITY",   # "You've won", "last chance", lottery, prize
    "PERSISTENCE",       # "Don't disconnect", call maintenance pressure
    "SAFE_ADVICE",       # "Never share your OTP" — protective guidance (NOT a threat)
    "NORMAL_SERVICE",    # Routine, legitimate call content
    "UNKNOWN",           # Insufficient context to classify
]

# ── Scenario-level labels ───────────────────────────────────────────────────
# Applied to the overall call / dialogue scenario.

SCENARIO_LABELS = [
    "BANK_KYC",           # Bank KYC expiry, account freeze, OTP scam
    "DIGITAL_ARREST",     # Fake CBI/police/customs/ED arrest threat
    "UPI_REFUND",         # Fake refund, collect request, QR receive scam
    "REMOTE_SUPPORT",     # AnyDesk/TeamViewer "tech support" scam
    "COURIER_CUSTOMS",    # Fake parcel/customs duty/drug seizure
    "INVESTMENT",         # Fake investment return, trading scam
    "JOB_FEE",            # Job offer with advance fee
    "FAMILY_EMERGENCY",   # Impersonating a relative in danger
    "LEGITIMATE_BANK",    # Genuine bank fraud alert (must NOT be flagged)
    "LEGITIMATE_COURIER", # Genuine delivery notification (must NOT be flagged)
    "AMBIGUOUS",          # Cannot determine scam vs legitimate with confidence
]

# ── Severity map (utterance label → severity 1–5) ──────────────────────────
SEVERITY = {
    "SECRET_REQUEST":  5,
    "REMOTE_ACCESS":   5,
    "PAYMENT_REQUEST": 5,
    "ISOLATION":       4,
    "FEAR_THREAT":     4,
    "AUTHORITY_CLAIM": 3,
    "URGENCY":         3,
    "SCREEN_SHARE":    3,
    "CHANNEL_SWITCH":  2,
    "REWARD_SCARCITY": 2,
    "PERSISTENCE":     2,
    "SAFE_ADVICE":     0,
    "NORMAL_SERVICE":  0,
    "UNKNOWN":         0,
}

# ── Critical labels (trigger immediate hard-rule alert) ────────────────────
CRITICAL_LABELS = {"SECRET_REQUEST", "REMOTE_ACCESS", "PAYMENT_REQUEST"}
