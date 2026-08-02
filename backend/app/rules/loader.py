import os
from pathlib import Path
from typing import Any

import yaml

from backend.app.rules.models import RuleDefinition, TemporalRuleDefinition


def load_rules_from_yaml(rules_dir: str | Path) -> list[RuleDefinition]:
    rules_dir = Path(rules_dir)
    if not rules_dir.exists():
        return []
    rules: list[RuleDefinition] = []
    for yaml_file in sorted(rules_dir.glob("*.yaml")):
        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, list):
            continue
        for item in data:
            if _is_temporal(item):
                continue
            rule = RuleDefinition(
                id=str(item.get("id", "")),
                version=int(item.get("version", 1)),
                enabled=bool(item.get("enabled", True)),
                languages=item.get("languages", ["en", "hi", "hi-en"]),
                description=str(item.get("description", "")),
                label=str(item.get("label", "")),
                severity=int(item.get("severity", 1)),
                confidence=float(item.get("confidence", 0.99)),
                score_delta=int(item.get("score_delta", 0)),
                risk_floor=int(item["risk_floor"]) if item.get("risk_floor") is not None else None,
                cooldown_seconds=int(item.get("cooldown_seconds", 0)),
                action_code=str(item.get("action_code", "")),
                explanation_code=str(item.get("explanation_code", "")),
                conditions=item.get("conditions", {}),
                exclusions=item.get("exclusions", {}),
            )
            rules.append(rule)
    return rules


def load_temporal_rules_from_yaml(rules_dir: str | Path) -> list[TemporalRuleDefinition]:
    rules_dir = Path(rules_dir)
    if not rules_dir.exists():
        return []
    rules: list[TemporalRuleDefinition] = []
    for yaml_file in sorted(rules_dir.glob("*.yaml")):
        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, list):
            continue
        for item in data:
            if not _is_temporal(item):
                continue
            rule = TemporalRuleDefinition(
                id=str(item.get("id", "")),
                version=int(item.get("version", 1)),
                enabled=bool(item.get("enabled", True)),
                within_seconds=int(item.get("within_seconds", 30)),
                requires=item.get("requires", []),
                optional=item.get("optional", []),
                severity=int(item.get("severity", 3)),
                score_delta=int(item.get("score_delta", 10)),
                risk_floor=int(item["risk_floor"]) if item.get("risk_floor") is not None else None,
            )
            rules.append(rule)
    return rules


def _is_temporal(item: dict[str, Any]) -> bool:
    return "within_seconds" in item or "requires" in item
