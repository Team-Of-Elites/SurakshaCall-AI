import re
from typing import List

SAFE_NEGATION_PATTERNS = [
    re.compile(r"(never|don.?t|do not|never ever|kabhi|कभी).{0,30}(share|give|tell|disclose|batana|batao|bataiye|bataen|dena|दो|बताओ|बताइए|बताएं|बताना).{0,30}(otp|pin|cvv|password|code|credential|पिन|कोड)", re.I),
    re.compile(r"(otp|pin|cvv|password|code|पिन|कोड).{0,30}(never|don.?t|do not|kabhi|कभी|nahi|नहीं|mat|मत).{0,30}(share|give|tell|disclose|batana|batao|bataiye|bataen|dena|दो|बताओ|बताइए|बताएं|बताना)", re.I),
    re.compile(r"(kabhi|कभी).{0,30}(otp|pin|code|पिन|कोड).{0,30}(mat|nahi|मत|नहीं).{0,30}(batana|batao|bataiye|bataen|dena|बताओ|बताइए|बताएं|बताना|दो|देना)", re.I),
    re.compile(r"(bank|staff|officer|employee|we|hum|हम).{0,40}(never|kabhi|कभी|nahi|नहीं).{0,20}(ask|request|demand|mangte|mangta|पूछते|माँगते)", re.I),
    re.compile(r"(protect|keep|save|guard|बचाओ|रखो).{0,20}(your\s*)?(otp|pin|password|code|cvv|पिन|कोड)", re.I),
    re.compile(r"(legitimate|real|official|genuine|असली|सरकारी).{0,30}(never|kabhi|कभी).{0,20}(ask|request|mangte|माँगते)", re.I),
    re.compile(r"(be\s*careful|beware|stay\s*alert|caution|सावधान).{0,40}(otp|pin|cvv|password|code|पिन|कोड)", re.I),
    re.compile(r"(report|call|contact|सूचना|रिपोर्ट).{0,20}(1930|cybercrime|police|helpline|साइबर|पुलिस)", re.I),
    re.compile(r"(will not|won't|cannot|can't|nahi|नहीं).{0,20}(share|give|tell|bataunga|bataungi|dunga|dungi|batana|दूंगा|बताऊंगा)", re.I),
]

SAFE_QUESTION_PATTERNS = [
    re.compile(r"(did\s*you|have\s*you|kya|क्या).{0,20}(receive|get|mila|aaya|aayi|मिला|आया).{0,15}(otp|code|pin|message|कोड)", re.I),
    re.compile(r"(if\s*(any|some)one|agar\s*koi|अगर\s*कोई).{0,30}(asks?|request|mange|माँगे).{0,15}(otp|pin|cvv|password|code|पिन|कोड)", re.I),
    re.compile(r"no\s*need\s*to\s*(share|give|tell|send|बताना|देना)", re.I),
]

SAFE_REPORTING_PATTERNS = [
    re.compile(r"(report|call|contact|visit|सूचित|कॉल).{0,20}(cybercrime|cyber\s*crime|1930|police|helpline|साइबर|पुलिस|हेल्पलाइन)", re.I),
    re.compile(r"(hang\s*up|disconnect|call\s*cut|कॉल\s*काट|काटो).{0,20}(report|complain|सूचना|रिपोर्ट)", re.I),
]


def is_safe_advice(text: str) -> bool:
    for pattern in SAFE_NEGATION_PATTERNS:
        if pattern.search(text):
            return True
    for pattern in SAFE_QUESTION_PATTERNS:
        if pattern.search(text):
            return True
    for pattern in SAFE_REPORTING_PATTERNS:
        if pattern.search(text):
            return True
    return False


def filter_safe_advice(text: str, detected_labels: List[str]) -> List[str]:
    if is_safe_advice(text):
        critical_to_remove = {"SECRET_REQUEST", "PAYMENT_REQUEST", "REMOTE_ACCESS", "FEAR_THREAT"}
        filtered = [
            label for label in detected_labels
            if label not in critical_to_remove
        ]
        if "SAFE_ADVICE" not in filtered:
            filtered.append("SAFE_ADVICE")
        return filtered
    return detected_labels
