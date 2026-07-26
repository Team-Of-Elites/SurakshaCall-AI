import pytest
from backend.app.privacy.redaction import Redactor
from backend.app.privacy.retention import RetentionManager, RetentionMode

def test_redact_aadhaar():
    raw_text = "My Aadhaar number is 1234 5678 9012 and you must verify it."
    redacted = Redactor.redact_transcript(raw_text)
    assert "[AADHAAR_REDACTED]" in redacted
    assert "1234 5678 9012" not in redacted

def test_redact_pan_card():
    raw_text = "Please check my PAN ABCDE1234F for the tax return."
    redacted = Redactor.redact_transcript(raw_text)
    assert "[PAN_REDACTED]" in redacted
    assert "ABCDE1234F" not in redacted

def test_redact_otp():
    raw_text = "Your OTP to login is 482193. Do not share this."
    redacted = Redactor.redact_transcript(raw_text)
    assert "[OTP_REDACTED]" in redacted
    assert "482193" not in redacted

def test_retention_modes():
    manager = RetentionManager(mode=RetentionMode.MAXIMUM_PRIVACY)
    # In maximum privacy, transcripts must NOT be saved to DB
    assert manager.should_save_transcript() is False
    assert manager.should_save_audio() is False
    
    manager.set_mode(RetentionMode.EVALUATION)
    # In evaluation mode, redacted transcripts are saved
    assert manager.should_save_transcript() is True
    assert manager.should_save_audio() is False # Audio is NEVER saved
