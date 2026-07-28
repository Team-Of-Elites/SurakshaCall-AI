SAFE_ADVICE_PATTERNS: list[str] = [
    r"(never|kabhi\s*mat|कभी\s*मत).{0,40}(share|give|tell|batana|दो|बताओ)",
    r"(bank|staff|officer|company|hum|हम).{0,40}(never|kabhi|कभी).{0,20}(ask|request|mangte|पूछते)",
    r"(protect|keep|guard|save|बचाओ|रखो).{0,20}(otp|pin|password|code|पिन)",
    r"(report|call|contact).{0,20}(cybercrime|1930|helpline|police)",
    r"(legitimate|real|official|genuine|असली|सरकारी).{0,30}(never|कभी).{0,20}(ask|request|माँगते)",
]

REFUSAL_PATTERNS: list[str] = [
    r"(will not|won't|cannot|can't).{0,20}(share|give|tell|provide)",
    r"(nahi|नहीं).{0,20}(bataunga|bataungi|dunga|dungi|karunga|karungi)",
]

QUESTION_PATTERNS: list[str] = [
    r"^(did|have|has|is|are|was|were|can|could|will|would|kya|क्या)",
    r"\?$",
    r"(did you|have you|kya aap|क्या आप).{0,30}(receive|get|share|give|batao|बताओ)",
]

REPORT_PATTERNS: list[str] = [
    r"(said|told|called|asked|requested|yesterday|earlier|last|previous|bola|bulaaya|कहा|बुलाया)",
]


def is_excluded_by_speech_act(text: str, speech_act: str) -> bool:
    import re
    if speech_act == "ADVICE":
        return any(re.search(p, text, re.I) for p in SAFE_ADVICE_PATTERNS)
    if speech_act == "REFUSAL":
        return any(re.search(p, text, re.I) for p in REFUSAL_PATTERNS)
    if speech_act == "QUESTION":
        return True
    if speech_act == "REPORT":
        return True
    return False
