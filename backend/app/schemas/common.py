# backend/app/schemas/common.py
#Namit added these files

from enum import StrEnum


class EvidenceSource(StrEnum):
    HARD_RULE = "hard_rule"
    CLASSIFIER = "classifier"
    LLM = "llm"
    IDENTITY = "identity"
    COMMUNITY = "community"
    SYSTEM = "system"


class ScoreDimension(StrEnum):
    SENSITIVE = "sensitive"
    MANIPULATION = "manipulation"
    FINANCIAL = "financial"
    IDENTITY = "identity"
    COMMUNITY = "community"
    ESCALATION = "escalation"


class RiskLevel(StrEnum):
    LOW = "LOW"
    CAUTION = "CAUTION"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProcessingMode(StrEnum):
    RULES_ONLY = "rules_only"
    RULES_AND_ML = "rules_and_ml"
    HYBRID_LOCAL = "hybrid_local"
    HYBRID_CLOUD_REDACTED = "hybrid_cloud_redacted"