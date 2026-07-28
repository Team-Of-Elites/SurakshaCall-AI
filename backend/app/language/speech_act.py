import re
from typing import Literal

SpeechAct = Literal["REQUEST", "COMMAND", "ADVICE", "REFUSAL", "QUESTION", "REPORT", "STATEMENT", "UNKNOWN"]

REQUEST_VERBS = [
    "share", "give", "tell", "send", "read", "provide", "confirm",
    "submit", "enter", "type", "say", "batao", "bataiye", "do", "karo",
    "दो", "दीजिए", "बताओ", "बताइए", "करो", "कीजिए",
]

COMMAND_INDICATORS = [
    "must", "need to", "have to", "required", "should",
    "chahiye", "hoga", "पड़ेगा", "चाहिए", "होगा",
]

ADVICE_INDICATORS = [
    "never", "should not", "shouldn't", "do not", "don't",
    "always", "remember", "kabhi mat", "kabhi bhi mat",
    "कभी मत", "कभी भी मत", "याद रखना",
]

REFUSAL_INDICATORS = [
    "will not", "won't", "cannot", "can't", "will never",
    "nahi karunga", "nahi karungi", "nahi bataunga", "nahi dungi",
    "नहीं करूंगा", "नहीं बताऊंगा", "नहीं दूंगा",
]

QUESTION_MARKERS = [
    "?", "what", "when", "where", "why", "how", "did", "does", "do",
    "have", "has", "is", "are", "was", "were", "can", "could",
    "will", "would", "shall", "should", "kya", "kaun", "kyun",
    "क्या", "कौन", "क्यों", "कहाँ", "कब",
]

REPORT_INDICATORS = [
    "said", "told", "called", "asked", "requested", "yesterday",
    "earlier", "last", "previous", "before", "happened",
    "bola tha", "bulaaya tha", "कहा था", "बुलाया था",
]


def classify_speech_act(text: str) -> SpeechAct:
    lower = text.lower().strip()
    if not lower:
        return "UNKNOWN"

    has_request = any(v in lower for v in REQUEST_VERBS) and not _is_safe_advice(lower)
    has_command = any(v in lower for v in COMMAND_INDICATORS)
    has_advice = any(v in lower for v in ADVICE_INDICATORS)
    has_refusal = any(v in lower for v in REFUSAL_INDICATORS)
    has_question = any(v in lower for v in QUESTION_MARKERS)
    has_report = any(v in lower for v in REPORT_INDICATORS)

    if has_refusal:
        return "REFUSAL"
    if has_advice or _is_safe_advice(lower):
        return "ADVICE"
    if has_report:
        return "REPORT"
    if has_question or lower.endswith("?"):
        return "QUESTION"
    if has_request or has_command:
        return "REQUEST"
    if _is_imperative(lower):
        return "COMMAND"
    return "STATEMENT"


def _is_safe_advice(text: str) -> bool:
    patterns = [
        r"(never|kabhi\s*mat|कभी\s*मत).{0,40}(share|give|tell|batana|दो|बताओ)",
        r"(bank|staff|company|hum|हम).{0,40}(never|kabhi|कभी).{0,20}(ask|request|mangte|पूछते)",
        r"(protect|keep|guard|save|बचाओ|रखो).{0,20}(otp|pin|password|code|पिन)",
    ]
    return any(re.search(p, text, re.I) for p in patterns)


def _is_imperative(text: str) -> bool:
    imperative_starts = [
        r"^(please\s+)?(do|tell|give|show|send|read|install|open|share|transfer|scan)",
        r"^(कृपया\s+)?(करो|दो|दिखाओ|भेजो|पढ़ो|खोलो)",
    ]
    return any(re.match(p, text, re.I) for p in imperative_starts)
