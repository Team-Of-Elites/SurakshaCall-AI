"""
SurakshaCall AI — Rule Engine Tests
Owner: Lakshay
Run: pytest tests/test_rules.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.detection.service import detect


# ── CRITICAL: Must ALWAYS detect ────────────────────────────────────────────

def test_direct_otp_english():
    result = detect("Please share your OTP with me right now.")
    assert "SECRET_REQUEST" in result.detected_labels
    assert result.is_critical

def test_indirect_six_digit_code():
    result = detect("Tell me the six digit code you received in the message.")
    assert "SECRET_REQUEST" in result.detected_labels
    assert result.is_critical

def test_hindi_otp_request():
    result = detect("Sir jo code aaya hai message mein woh bataiye.")
    assert "SECRET_REQUEST" in result.detected_labels

def test_romanized_hindi_code():
    result = detect("Abhi jo chhe ank aaye hain woh bolo.")
    assert "SECRET_REQUEST" in result.detected_labels

def test_anydesk_remote_access():
    result = detect("Please install AnyDesk on your phone so I can help you.")
    assert "REMOTE_ACCESS" in result.detected_labels
    assert result.is_critical

def test_upi_collect_request():
    result = detect("Please approve the UPI collect request I just sent you.")
    assert "PAYMENT_REQUEST" in result.detected_labels
    assert result.is_critical

def test_isolation_hindi():
    result = detect("Kisi ko mat batana, yeh confidential case hai.")
    assert "ISOLATION" in result.detected_labels

def test_cbi_authority_claim():
    result = detect("Namaste, main CBI officer bol raha hoon.")
    assert "AUTHORITY_CLAIM" in result.detected_labels

def test_arrest_threat():
    result = detect("A non-bailable warrant has been issued in your name.")
    assert "FEAR_THREAT" in result.detected_labels

def test_urgency_time_pressure():
    result = detect("You must transfer the amount within 10 minutes.")
    assert "URGENCY" in result.detected_labels


# ── SAFE ADVICE: Must NOT trigger critical labels ────────────────────────────

def test_safe_advice_never_share_otp():
    result = detect("Never share your OTP with anyone, not even bank staff.")
    assert "SECRET_REQUEST" not in result.detected_labels
    assert result.safe_advice_detected

def test_safe_advice_bank_never_asks():
    result = detect("Real bank officers never ask for your PIN or CVV over the phone.")
    assert "SECRET_REQUEST" not in result.detected_labels

def test_legitimate_bank_call_not_flagged():
    result = detect("Hello, this is a fraud alert from your bank. We noticed unusual activity.")
    # Should NOT be critical (no specific demand made)
    labels = result.detected_labels
    assert "SECRET_REQUEST" not in labels
    assert "PAYMENT_REQUEST" not in labels
    assert "REMOTE_ACCESS" not in labels
