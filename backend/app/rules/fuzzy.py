import re
from difflib import SequenceMatcher

from backend.app.language.lexicon import CONCEPT_ALIASES


def fuzzy_match_concept(text: str, concept_name: str) -> float:
    best = 0.0
    concept_upper = concept_name.upper()
    aliases = CONCEPT_ALIASES.get(concept_upper, [concept_name.lower()])
    for alias in aliases:
        ratio = SequenceMatcher(None, text.lower(), alias.lower()).ratio()
        best = max(best, ratio)
        if alias.lower() in text.lower():
            return 1.0
        words = alias.lower().split()
        text_words = text.lower().split()
        if len(words) <= 3:
            alias_joined = "".join(words)
            for i in range(len(text_words) - len(words) + 1):
                chunk = "".join(text_words[i:i + len(words)])
                if chunk == alias_joined:
                    return 0.95
    return best


def fuzzy_match_phrase(text: str, phrase: str, threshold: float = 0.85) -> tuple[bool, float]:
    ratio = SequenceMatcher(None, text.lower(), phrase.lower()).ratio()
    if ratio >= threshold:
        return True, ratio
    return False, ratio
