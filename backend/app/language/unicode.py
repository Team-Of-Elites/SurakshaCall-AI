import re
import unicodedata


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def clean_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_punctuation(text: str) -> str:
    text = re.sub(r"[،؛]+", ",", text)
    text = re.sub(r"[؟]+", "?", text)
    text = re.sub(r"[।॥]+", ".", text)
    text = re.sub(r"[「」『』]+", '"', text)
    return text


def strip_diacritics(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def is_devanagari(char: str) -> bool:
    cp = ord(char)
    return 0x0900 <= cp <= 0x097F


def contains_devanagari(text: str) -> bool:
    return any(is_devanagari(c) for c in text)


def detect_script(text: str) -> str:
    devanagari_count = sum(1 for c in text if is_devanagari(c))
    latin_count = sum(1 for c in text if c.isascii() and c.isalpha())
    if devanagari_count > latin_count:
        return "devanagari"
    if latin_count > 0:
        return "latin"
    return "other"
