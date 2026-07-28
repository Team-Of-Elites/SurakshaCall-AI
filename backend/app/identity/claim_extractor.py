import re
from typing import Any

from backend.app.identity.aliases import ALIAS_MAP

CLAIM_PATTERNS: list[str] = [
    r"(?:i am|i'm|main|मैं)\s+(?:calling from|speaking from|from|se bol raha|se bol rahi|se call kar|हूँ|है)\s*([A-Za-z\s]+)",
    r"(?:this is|yeh|यह)\s+([A-Za-z\s]+)\s+(?:department|calling|team|office|का कार्यालय|से बोल)",
    r"(?:your bank|aapke bank|आपके बैंक)\s+([A-Za-z\s]+)\s+(?:team|department|se|से)",
    r"(?:i am|main|मैं)\s+(?:inspector|officer|representative|employee|agent)\s+(?:of|from|se|का)\s*([A-Za-z\s]+)",
]

ENTITY_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b(cbi|sbi|rbi|hdfc|icici|axis|pnb|trai|ed|आरबीआई|सीबीआई)\b", re.I),
]


def extract_claims(text: str) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    seen_orgs: set[str] = set()

    for pattern in CLAIM_PATTERNS:
        m = re.search(pattern, text, re.I)
        if m:
            org_text = m.group(1).strip() if m.lastindex and m.group(1) else ""
            if org_text and len(org_text) < 60 and org_text.lower() not in seen_orgs:
                seen_orgs.add(org_text.lower())
                canonical = _resolve_canonical(org_text)
                claims.append({
                    "organization_text": org_text,
                    "canonical_organization": canonical,
                    "evidence_quote": m.group(0)[:80],
                    "confidence": 0.85,
                })

    for pattern in ENTITY_PATTERNS:
        for m in pattern.finditer(text.lower()):
            org = m.group(0).lower()
            if org not in seen_orgs:
                seen_orgs.add(org)
                canonical = _resolve_canonical(org)
                claims.append({
                    "organization_text": m.group(0),
                    "canonical_organization": canonical,
                    "evidence_quote": m.group(0),
                    "confidence": 0.5,
                })

    return claims


def _resolve_canonical(org_text: str) -> str:
    key = org_text.lower().strip()
    return ALIAS_MAP.get(key, org_text)
