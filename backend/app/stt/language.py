"""
language.py — Task O-08: Hindi and Code-Mixed (Hinglish) Language Support

Handles language detection, code-mixed script normalization, and logging ASR errors for training.
"""

import re


def detect_code_mixing(text: str) -> dict:
    devanagari_count = len(re.findall(r"[\u0900-\u097F]", text))
    latin_count = len(re.findall(r"[a-zA-Z]", text))

    hinglish_keywords = {
        "kyc", "otp", "pin", "block", "account", "department", "bol", "raha",
        "hoon", "kijiye", "bataiye", "mat", "kisi", "pan", "card", "police", "cbi"
    }

    words = set(re.findall(r"\w+", text.lower()))
    hinglish_hits = words.intersection(hinglish_keywords)

    is_devanagari = devanagari_count > latin_count
    is_code_mixed = len(hinglish_hits) > 0 or (devanagari_count > 0 and latin_count > 0)

    primary_lang = "hi" if is_devanagari or len(hinglish_hits) >= 2 else "en"

    return {
        "text": text,
        "primary_language": primary_lang,
        "is_code_mixed": is_code_mixed,
        "devanagari_char_count": devanagari_count,
        "latin_char_count": latin_count,
        "hinglish_keyword_matches": list(hinglish_hits),
    }
