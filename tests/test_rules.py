"""
SurakshaCall AI — Rule Engine Tests (English Only)
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

def test_verification_code_read_out():
    result = detect("I will send you a verification code. Please read it out to me immediately.")
    assert "SECRET_REQUEST" in result.detected_labels
    assert result.is_critical

def test_access_code_on_screen():
    result = detect("Once you install, give me the access code shown on screen. Do not close the application.")
    assert "SECRET_REQUEST" in result.detected_labels

def test_nine_digit_id():
    result = detect("Share the 9-digit ID on screen with me.")
    assert "SECRET_REQUEST" in result.detected_labels

def test_anydesk_remote_access():
    result = detect("Please install AnyDesk on your phone so I can help you.")
    assert "REMOTE_ACCESS" in result.detected_labels
    assert result.is_critical

def test_teamviewer_remote_access():
    result = detect("Please install TeamViewer QuickSupport on your phone right now.")
    assert "REMOTE_ACCESS" in result.detected_labels

def test_upi_collect_request():
    result = detect("Please approve the UPI collect request I just sent you.")
    assert "PAYMENT_REQUEST" in result.detected_labels
    assert result.is_critical

def test_safe_account_transfer():
    result = detect("You must transfer the funds to a safe account immediately.")
    assert "PAYMENT_REQUEST" in result.detected_labels

def test_qr_scan_refund_scam():
    result = detect("No sir, this is a special refund QR. Please scan it right now.")
    assert "PAYMENT_REQUEST" in result.detected_labels

def test_amount_transfer():
    result = detect("Transfer 50,000 rupees to the government account right now.")
    assert "PAYMENT_REQUEST" in result.detected_labels

def test_lakh_transfer():
    result = detect("You must pay 2 lakh immediately to clear the case.")
    assert "PAYMENT_REQUEST" in result.detected_labels

def test_isolation_dont_tell():
    result = detect("Do not tell anyone about this call, especially your family.")
    assert "ISOLATION" in result.detected_labels

def test_isolation_stay_on_line():
    result = detect("You must stay on the line. Do not disconnect this call.")
    assert "ISOLATION" in result.detected_labels

def test_cbi_authority_claim():
    result = detect("Hello, I am an officer from the CBI calling about your case.")
    assert "AUTHORITY_CLAIM" in result.detected_labels

def test_arrest_threat():
    result = detect("A non-bailable warrant has been issued in your name.")
    assert "FEAR_THREAT" in result.detected_labels

def test_account_freeze_threat():
    result = detect("Your account will be frozen within the next 2 hours.")
    assert "FEAR_THREAT" in result.detected_labels

def test_urgency_time_pressure():
    result = detect("You must transfer the amount within 10 minutes.")
    assert "URGENCY" in result.detected_labels

def test_screen_share():
    result = detect("Please share your screen so we can help you fix this.")
    assert "SCREEN_SHARE" in result.detected_labels


# ── SAFE ADVICE: Must NOT trigger critical labels ────────────────────────────

def test_safe_advice_never_share_otp():
    result = detect("Never share your OTP with anyone, not even bank staff.")
    assert "SECRET_REQUEST" not in result.detected_labels
    assert result.safe_advice_detected

def test_safe_advice_bank_never_asks():
    result = detect("Real bank officers never ask for your PIN or CVV over the phone.")
    assert "SECRET_REQUEST" not in result.detected_labels

def test_safe_advice_if_anyone_asks():
    result = detect("If anyone asks for your PIN, CVV, or password, hang up and report to cybercrime.")
    assert "SECRET_REQUEST" not in result.detected_labels
    assert result.safe_advice_detected

def test_safe_advice_question_otp():
    result = detect("Hello, did you receive an OTP from our system?")
    assert result.safe_advice_detected
    assert not result.is_critical

def test_legitimate_bank_call_not_flagged():
    result = detect("Hello, this is a fraud alert from your bank. We noticed unusual activity.")
    assert "SECRET_REQUEST" not in result.detected_labels
    assert "PAYMENT_REQUEST" not in result.detected_labels
    assert "REMOTE_ACCESS" not in result.detected_labels

def test_legitimate_no_need_to_share():
    result = detect("Good, that confirms your registration is complete. No need to share it with anyone.")
    assert not result.is_critical


# ── MULTI-LABEL: Verify multiple labels detected together ────────────────────

def test_multi_label_fear_plus_payment():
    result = detect("You will be arrested unless you pay a clearance fee of 75,000 rupees right now.")
    assert "FEAR_THREAT" in result.detected_labels
    assert "PAYMENT_REQUEST" in result.detected_labels
    assert result.trigger_llm

def test_multi_label_authority_plus_secret():
    result = detect("This is the CBI. Tell me the six digit code from the message you just received.")
    assert "AUTHORITY_CLAIM" in result.detected_labels
    assert "SECRET_REQUEST" in result.detected_labels

def test_multi_label_remote_plus_isolation():
    result = detect("Install AnyDesk right now. Do not tell anyone about this call.")
    assert "REMOTE_ACCESS" in result.detected_labels
    assert "ISOLATION" in result.detected_labels
