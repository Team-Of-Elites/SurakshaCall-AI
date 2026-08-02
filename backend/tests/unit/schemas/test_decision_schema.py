# backend/tests/unit/schemas/test_decision_schema.py
# Made by Namit

import pytest
from pydantic import ValidationError

from app.schemas.decision import RiskDecision


def test_risk_index_above_100_is_rejected(valid_decision_dict):
    valid_decision_dict["risk_index"] = 101

    with pytest.raises(ValidationError):
        RiskDecision.model_validate(valid_decision_dict)


def test_unknown_risk_level_is_rejected(valid_decision_dict):
    valid_decision_dict["risk_level"] = "DANGER"

    with pytest.raises(ValidationError):
        RiskDecision.model_validate(valid_decision_dict)


def test_unknown_field_is_rejected(valid_decision_dict):
    valid_decision_dict["fraud_confirmed"] = True

    with pytest.raises(ValidationError):
        RiskDecision.model_validate(valid_decision_dict)


def test_valid_decision_serializes(valid_decision_dict):
    decision = RiskDecision.model_validate(valid_decision_dict)

    output = decision.model_dump(mode="json")

    assert output["risk_index"] == 85
    assert output["risk_level"] == "CRITICAL"