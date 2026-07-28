from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuleDefinition:
    id: str
    version: int = 1
    enabled: bool = True
    languages: list[str] = field(default_factory=lambda: ["en", "hi", "hi-en"])
    description: str = ""
    label: str = ""
    severity: int = 1
    confidence: float = 0.99
    score_delta: int = 0
    risk_floor: int | None = None
    cooldown_seconds: int = 0
    action_code: str = ""
    explanation_code: str = ""
    conditions: dict[str, Any] = field(default_factory=dict)
    exclusions: dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalRuleDefinition:
    id: str
    version: int = 1
    enabled: bool = True
    within_seconds: int = 30
    requires: list[str] = field(default_factory=list)
    optional: list[str] = field(default_factory=list)
    severity: int = 3
    score_delta: int = 10
    risk_floor: int | None = None
