import re
from datetime import datetime, timezone
from typing import Any

from backend.app.language.lexicon import CONCEPT_ALIASES
from backend.app.language.normalizer import ConceptSpan, NormalizedUtterance
from backend.app.rules.fuzzy import fuzzy_match_concept
from backend.app.rules.models import RuleDefinition


class RuleMatch:
    def __init__(
        self,
        rule_id: str,
        label: str,
        confidence: float,
        severity: int,
        evidence_quote: str,
        score_delta: int = 0,
        risk_floor: int | None = None,
        source: str = "rule",
        action_code: str = "",
    ):
        self.rule_id = rule_id
        self.label = label
        self.confidence = confidence
        self.severity = severity
        self.evidence_quote = evidence_quote
        self.score_delta = score_delta
        self.risk_floor = risk_floor
        self.source = source
        self.action_code = action_code


def evaluate_rules(
    normalized: NormalizedUtterance,
    rules: list[RuleDefinition],
    recent_labels: list[str] | None = None,
) -> list[RuleMatch]:
    matches: list[RuleMatch] = []
    seen_labels: set[str] = set()
    text = normalized.normalized_text
    concepts = {c.concept for c in normalized.concepts}

    for rule in rules:
        if not rule.enabled:
            continue
        if normalized.language_mode not in rule.languages and "all" not in rule.languages:
            continue
        if rule.label in seen_labels:
            continue

        label = rule.label
        conditions = rule.conditions
        if not conditions:
            continue

        match_found = False
        evidence_quote = ""
        score = 1.0

        all_cond = conditions.get("all", [])
        any_cond = conditions.get("any", [])

        if all_cond:
            match_found = True
            for cond in all_cond:
                cond_match, cond_score, cond_quote = _evaluate_condition(cond, text, concepts, normalized)
                if not cond_match:
                    match_found = False
                    break
                score = min(score, cond_score)
                if cond_quote:
                    evidence_quote = cond_quote

        if any_cond and not match_found:
            for cond in any_cond:
                cond_match, cond_score, cond_quote = _evaluate_condition(cond, text, concepts, normalized)
                if cond_match:
                    match_found = True
                    score = cond_score
                    evidence_quote = cond_quote or evidence_quote
                    break

        if not match_found:
            continue

        exclusions = rule.exclusions
        if _check_exclusions(exclusions, text, concepts, normalized.speech_act):
            continue

        seen_labels.add(label)
        matches.append(RuleMatch(
            rule_id=rule.id,
            label=label,
            confidence=score * rule.confidence,
            severity=rule.severity,
            evidence_quote=evidence_quote or text[:80],
            score_delta=rule.score_delta,
            risk_floor=rule.risk_floor,
            action_code=rule.action_code,
        ))

    return matches


def _evaluate_condition(
    cond: dict[str, Any],
    text: str,
    concepts: set[str],
    normalized: NormalizedUtterance,
) -> tuple[bool, float, str]:
    cond_type = cond.get("type", "concept")
    value = cond.get("value", "")
    alias = cond.get("alias", "")

    if cond_type == "concept":
        return _match_concept(concepts, value, text, alias)
    elif cond_type == "regex":
        return _match_regex(text, value, alias)
    elif cond_type == "speech_act":
        return (normalized.speech_act == value, 1.0, "")
    return (False, 0.0, "")


def _match_concept(concepts: set[str], concept_name: str, text: str, alias: str = "") -> tuple[bool, float, str]:
    if concept_name in concepts:
        return (True, 1.0, text[:80])
    for cname, aliases in CONCEPT_ALIASES.items():
        if concept_name.upper() == cname:
            for a in aliases:
                if a and re.search(r"\b" + re.escape(a.lower()) + r"\b", text.lower()):
                    return (True, 1.0, a)
    fuzzy = fuzzy_match_concept(text, concept_name)
    if fuzzy > 0.75:
        return (True, fuzzy, text[:60])
    return (False, 0.0, "")


def _match_regex(text: str, pattern: str, label: str = "") -> tuple[bool, float, str]:
    try:
        m = re.search(pattern, text, re.I)
        if m:
            return (True, 1.0, m.group(0))
    except re.error:
        pass
    return (False, 0.0, "")


def _check_exclusions(
    exclusions: dict[str, Any],
    text: str,
    concepts: set[str],
    speech_act: str,
) -> bool:
    any_excl = exclusions.get("any", [])
    for excl in any_excl:
        etype = excl.get("type", "concept")
        evalue = excl.get("value", "")
        if etype == "speech_act" and speech_act == evalue:
            return True
        if etype == "concept" and evalue in concepts:
            return True
        if etype == "regex" and re.search(evalue, text, re.I):
            return True
    return False
