import re
from typing import Literal

from backend.app.language.lexicon import ASR_CORRECTIONS, CONCEPT_ALIASES
from backend.app.language.speech_act import SpeechAct, classify_speech_act
from backend.app.language.unicode import (
    clean_whitespace,
    contains_devanagari,
    normalize_punctuation,
    normalize_unicode,
)

LanguageMode = Literal["en", "hi", "hi-en", "unknown"]

ROMAN_HINT_WORDS = {
    "aapka", "aapke", "aapko", "aapse", "aap", "main", "hu", "hoon",
    "hai", "hain", "tha", "the", "raha", "rahi", "rahe",
    "mujhe", "tum", "tumhe", "tere", "mera", "meri", "mere",
    "karo", "karein", "karta", "karti", "kiya", "kare",
    "jao", "jaayega", "jaa", "jata", "jaati",
    "batao", "bataiye", "bata", "batana", "bolo", "bolraha", "bolrah",
    "nahi", "na", "mat", "kya", "kaun", "kyun", "kahan", "kab",
    "apna", "apni", "apne", "inka", "unki", "unka",
    "wala", "wali", "wale", "lo", "do", "de", "dena", "dijiye",
    "sir", "ji", "hoga", "hogee", "sakta", "sakti", "sakte",
    "chahiye", "hona", "sakta", "karunga", "karungi",
    "bhejo", "bhej", "aaya", "aayi", "gaya", "gayi",
    "manga", "mangte", "mangta", "mangi",
}


class ConceptSpan:
    def __init__(self, concept: str, start_char: int, end_char: int, confidence: float = 1.0):
        self.concept = concept
        self.start_char = start_char
        self.end_char = end_char
        self.confidence = confidence


class NormalizedUtterance:
    def __init__(
        self,
        raw_text: str,
        normalized_text: str,
        redacted_text: str,
        language_mode: LanguageMode = "en",
        speech_act: SpeechAct = "STATEMENT",
        concepts: list[ConceptSpan] | None = None,
        transcript_quality: float = 1.0,
    ):
        self.raw_text = raw_text
        self.normalized_text = normalized_text
        self.redacted_text = redacted_text
        self.language_mode = language_mode
        self.speech_act = speech_act
        self.concepts = concepts or []
        self.transcript_quality = transcript_quality


REDACT_PATTERNS: list[tuple[str, str]] = [
    (r"\b\d{4,8}\b", "[SECRET_CODE]"),
    (r"\b\d{10,12}\b", "[PHONE_NUMBER]"),
    (r"\b[A-Z]{5}\d{4}[A-Z]\b", "[PAN]"),
    (r"\b\d{12}\b", "[AADHAAR]"),
    (r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[EMAIL]"),
    (r"\b(?:\+?91[\-\s]?)?[6-9]\d{9}\b", "[PHONE_NUMBER]"),
]


HI_EN_TRANSLITERATION = {
    "पिन": "pin", "कोड": "code", "खाता": "account", "बैंक": "bank",
    "फ्रीज": "freeze", "ब्लॉक": "block", "ओटीपी": "otp",
    "गोपनीय": "secret", "सत्यापन": "verification", "कृपया": "please",
    "पासवर्ड": "password", "कार्ड": "card", "नंबर": "number",
    "रुपये": "rupees", "पैसे": "money", "भुगतान": "payment",
    "गिरफ्तार": "arrest", "वारंट": "warrant", "कोर्ट": "court",
    "जेल": "jail", "केस": "case", "एफआईआर": "fir",
    "सीबीआई": "cbi", "आरबीआई": "rbi", "पुलिस": "police",
    "साइबर": "cyber", "क्राइम": "crime",
    "खाता": "account", "बंद": "close", "होगा": "hoga",
    "जाएगा": "jaayega", "सकता": "sakta",
}


def normalize(raw_text: str, language: str | None = None) -> NormalizedUtterance:
    raw = raw_text.strip()

    unicode_normalized = normalize_unicode(raw)
    cleaned = clean_whitespace(normalize_punctuation(unicode_normalized))
    lower = cleaned.lower()

    has_deva = contains_devanagari(lower)
    has_latin = bool(re.search(r"[a-zA-Z]", lower))
    has_roman_hindi = _detect_roman_hindi(lower)

    if has_deva and has_latin:
        mode: LanguageMode = "hi-en"
    elif has_deva:
        mode = "hi"
        lower = _transliterate_devanagari(lower)
    elif has_roman_hindi:
        mode = "hi-en"
    elif has_latin:
        mode = "en"
    else:
        mode = "unknown"

    for wrong, correct in ASR_CORRECTIONS.items():
        lower = re.sub(r"\b" + re.escape(wrong) + r"\b", correct, lower)

    redacted = lower
    for pattern, placeholder in REDACT_PATTERNS:
        redacted = re.sub(pattern, placeholder, redacted)

    concepts: list[ConceptSpan] = []
    for concept_name, aliases in CONCEPT_ALIASES.items():
        for alias in aliases:
            if not alias:
                continue
            if re.search(r"\b" + re.escape(alias.lower()) + r"\b", lower):
                idx = lower.find(alias.lower())
                concepts.append(ConceptSpan(
                    concept=concept_name,
                    start_char=idx,
                    end_char=idx + len(alias),
                ))
                break

    speech_act = classify_speech_act(raw)

    return NormalizedUtterance(
        raw_text=raw,
        normalized_text=lower,
        redacted_text=redacted,
        language_mode=mode,
        speech_act=speech_act,
        concepts=concepts,
    )


def _detect_roman_hindi(text: str) -> bool:
    words = set(text.lower().split())
    matches = words & ROMAN_HINT_WORDS
    return len(matches) >= 1


def _transliterate_devanagari(text: str) -> str:
    for deva, eng in HI_EN_TRANSLITERATION.items():
        text = text.replace(deva, eng)
    return text
