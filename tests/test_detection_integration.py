"""Integration tests: detection service + language + YAML rules."""
from backend.app.detection.service import detect


def test_direct_otp():
    result = detect("Please share your OTP with me.")
    assert "SECRET_REQUEST" in result.detected_labels
    assert result.is_critical


def test_indirect_code():
    result = detect("Tell me the six digit code from the message.")
    assert "SECRET_REQUEST" in result.detected_labels
    assert result.is_critical


def test_safe_advice():
    result = detect("Never share your OTP with anyone.")
    assert "SAFE_ADVICE" in result.detected_labels
    assert not result.is_critical


def test_hindi_otp():
    result = detect("कृपया अपना OTP बताइए।")
    assert "SECRET_REQUEST" in result.detected_labels


def test_hindi_secret_code():
    result = detect("फोन पर आया छह अंक का कोड बताइए।")
    assert "SECRET_REQUEST" in result.detected_labels


def test_hindi_authority():
    result = detect("मैं CBI से बोल रहा हूँ।")
    assert "AUTHORITY_CLAIM" in result.detected_labels


def test_hindi_threat():
    result = detect("आपका खाता फ्रीज हो जाएगा।")
    assert "FEAR_THREAT" in result.detected_labels


def test_hindi_safe_advice():
    result = detect("कभी भी अपना OTP किसी को मत बताएं।")
    assert "SAFE_ADVICE" in result.detected_labels
    assert not result.is_critical


def test_code_mixed():
    result = detect("Sir, aapka account freeze ho jayega. OTP batao jaldi.")
    labels = result.detected_labels
    assert "SECRET_REQUEST" in labels
    assert "FEAR_THREAT" in labels


def test_remote_access():
    result = detect("Install AnyDesk and give me the code.")
    assert "REMOTE_ACCESS" in result.detected_labels
    assert result.is_critical


def test_payment_request():
    result = detect("Transfer 50,000 rupees to safe account immediately.")
    assert "PAYMENT_REQUEST" in result.detected_labels
    assert result.is_critical


def test_isolation():
    result = detect("Kisi ko mat batana. Call mat cut karna.")
    assert "ISOLATION" in result.detected_labels


def test_legitimate_call():
    result = detect("Your parcel will be delivered tomorrow between 2 and 5 PM.")
    assert not result.is_critical
    assert len(result.detected_labels) == 0


def test_user_refusal():
    result = detect("I will not share my OTP with you.")
    assert "SECRET_REQUEST" not in result.detected_labels
    assert not result.is_critical


def test_hindi_user_refusal():
    result = detect("मैं अपना OTP नहीं बताऊंगा।")
    assert "SECRET_REQUEST" not in result.detected_labels
    assert not result.is_critical
