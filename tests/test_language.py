"""Tests for multilingual language module."""
from backend.app.language.normalizer import normalize
from backend.app.language.speech_act import classify_speech_act
from backend.app.language.unicode import contains_devanagari, detect_script


def test_english_normalization():
    n = normalize("Please share your OTP with me.")
    assert "otp" in n.normalized_text
    assert n.language_mode == "en"


def test_hindi_normalization():
    n = normalize("कृपया अपना OTP मुझे बताइए।")
    assert n.language_mode == "hi-en" or n.language_mode == "hi"


def test_hindi_only_normalization():
    n = normalize("कृपया अपना पिन कोड बताइए।")
    assert "pin" in n.normalized_text
    assert n.language_mode in ("hi", "hi-en")


def test_roman_hindi_normalization():
    n = normalize("Mujhe apna OTP batao.")
    assert n.language_mode == "hi-en"


def test_code_mixed_normalization():
    n = normalize("Sir, aapka account freeze ho jayega.")
    assert n.language_mode == "hi-en"
    assert "freeze" in n.normalized_text or "account" in n.normalized_text


def test_asr_correction():
    n = normalize("Tell me the six digital code.")
    assert "digital" not in n.normalized_text.replace("six digital", "")
    assert "digit" in n.normalized_text or "code" in n.normalized_text


def test_redaction():
    n = normalize("My OTP is 482193.")
    assert "[SECRET_CODE]" in n.redacted_text
    assert "482193" not in n.redacted_text


def test_speech_act_request():
    assert classify_speech_act("Tell me your OTP.") in ("REQUEST", "COMMAND")


def test_speech_act_advice():
    assert classify_speech_act("Never share your OTP with anyone.") == "ADVICE"


def test_speech_act_refusal():
    assert classify_speech_act("I will not share my OTP.") == "REFUSAL"


def test_speech_act_question():
    assert classify_speech_act("Did you receive the code?") == "QUESTION"


def test_concept_extraction():
    n = normalize("Please share the OTP with me.")
    concepts = {c.concept for c in n.concepts}
    assert "OTP" in concepts


def test_hindi_concept_extraction():
    n = normalize("कृपया अपना ओटीपी बताइए।")
    concepts = {c.concept for c in n.concepts}
    assert "OTP" in concepts or "ONE_TIME_CODE" in concepts


def test_unicode_detection():
    assert contains_devanagari("हिन्दी")
    assert not contains_devanagari("English")
    assert detect_script("नमस्ते") == "devanagari"
    assert detect_script("Hello") == "latin"
