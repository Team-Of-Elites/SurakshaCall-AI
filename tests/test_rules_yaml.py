"""Tests for YAML-based rule engine."""
from pathlib import Path

from backend.app.language.normalizer import normalize
from backend.app.rules.engine import evaluate_rules
from backend.app.rules.loader import load_rules_from_yaml, load_temporal_rules_from_yaml

RULES_DIR = Path(__file__).parent.parent / "data" / "rules"


def test_yaml_rules_load():
    rules = load_rules_from_yaml(RULES_DIR)
    assert len(rules) > 0
    rule_ids = [r.id for r in rules]
    assert "secret.direct_otp.v1" in rule_ids
    assert "manipulation.authority.v1" in rule_ids


def test_temporal_rules_load():
    rules = load_temporal_rules_from_yaml(RULES_DIR)
    assert len(rules) > 0
    rule_ids = [r.id for r in rules]
    assert "temporal.threat_payment_isolation.v1" in rule_ids


def test_yaml_rule_direct_otp():
    rules = load_rules_from_yaml(RULES_DIR)
    n = normalize("Please share your OTP with me.")
    matches = evaluate_rules(n, rules)
    labels = {m.label for m in matches}
    assert "SECRET_REQUEST" in labels


def test_yaml_rule_hindi_otp():
    rules = load_rules_from_yaml(RULES_DIR)
    n = normalize("कृपया अपना OTP बताइए।")
    matches = evaluate_rules(n, rules)
    labels = {m.label for m in matches}
    assert "SECRET_REQUEST" in labels


def test_yaml_rule_hindi_secret_request():
    rules = load_rules_from_yaml(RULES_DIR)
    n = normalize("फोन पर आया छह अंक का कोड बताइए।")
    matches = evaluate_rules(n, rules)
    labels = {m.label for m in matches}
    assert "SECRET_REQUEST" in labels


def test_yaml_rule_authority_claim():
    rules = load_rules_from_yaml(RULES_DIR)
    n = normalize("Main CBI se bol raha hoon.")
    matches = evaluate_rules(n, rules)
    labels = {m.label for m in matches}
    assert "AUTHORITY_CLAIM" in labels


def test_yaml_rule_fear_threat():
    rules = load_rules_from_yaml(RULES_DIR)
    n = normalize("Aapka account freeze ho jayega.")
    matches = evaluate_rules(n, rules)
    labels = {m.label for m in matches}
    assert "FEAR_THREAT" in labels


def test_yaml_rule_safe_advice():
    rules = load_rules_from_yaml(RULES_DIR)
    n = normalize("Never share your OTP with anyone.")
    matches = evaluate_rules(n, rules)
    safe_labels = {m.label for m in matches}
    assert "SAFE_ADVICE" in safe_labels
    assert "SECRET_REQUEST" not in safe_labels


def test_yaml_rule_payment():
    rules = load_rules_from_yaml(RULES_DIR)
    n = normalize("Transfer 50,000 rupees to safe account.")
    matches = evaluate_rules(n, rules)
    labels = {m.label for m in matches}
    assert "PAYMENT_REQUEST" in labels


def test_yaml_rule_remote_access():
    rules = load_rules_from_yaml(RULES_DIR)
    n = normalize("Install AnyDesk on your phone.")
    matches = evaluate_rules(n, rules)
    labels = {m.label for m in matches}
    assert "REMOTE_ACCESS" in labels


def test_yaml_rule_urgency():
    rules = load_rules_from_yaml(RULES_DIR)
    n = normalize("Do it right now or your account will be blocked.")
    matches = evaluate_rules(n, rules)
    labels = {m.label for m in matches}
    assert "URGENCY" in labels


def test_yaml_rule_isolation():
    rules = load_rules_from_yaml(RULES_DIR)
    n = normalize("Kisi ko mat batana.")
    matches = evaluate_rules(n, rules)
    labels = {m.label for m in matches}
    assert "ISOLATION" in labels


def test_yaml_rule_hindi_authority():
    rules = load_rules_from_yaml(RULES_DIR)
    n = normalize("मैं सीबीआई इंस्पेक्टर बोल रहा हूँ।")
    matches = evaluate_rules(n, rules)
    labels = {m.label for m in matches}
    assert "AUTHORITY_CLAIM" in labels


def test_yaml_rule_exclusion_safe_advice():
    """Safe advice must NOT trigger SECRET_REQUEST."""
    rules = load_rules_from_yaml(RULES_DIR)
    n = normalize("Bank employees never ask for your OTP.")
    matches = evaluate_rules(n, rules)
    labels = {m.label for m in matches}
    assert "SECRET_REQUEST" not in labels
