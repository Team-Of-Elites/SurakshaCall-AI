"""
SurakshaCall AI — Identity Verification & Phone Normalization Tests
Owner: Lakshay
Run: pytest tests/test_identity.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.identity.phone_numbers import normalize_phone
from backend.app.identity.verifier import verify_identity, IdentityStatus

def test_phone_normalization_valid_indian_mobile():
    info = normalize_phone("+919810012345")
    assert info.is_valid
    assert info.is_mobile
    assert info.e164 == "+919810012345"
    assert not info.is_voip

def test_phone_normalization_invalid():
    info = normalize_phone("12345")
    assert not info.is_valid

def test_phone_normalization_trai_160():
    info = normalize_phone("1600112211")
    assert info.is_trai_160

def test_identity_verified_official():
    result = verify_identity(
        phone_number="1800112211",
        claimed_org_name="SBI",
        detected_labels=["NORMAL_SERVICE"]
    )
    assert result.status == IdentityStatus.VERIFIED_OFFICIAL
    assert result.risk_contribution == 0
    assert result.in_trusted_directory

def test_identity_unverified_spoof_risk():
    result = verify_identity(
        phone_number="+919810012345",
        claimed_org_name="SBI",
        detected_labels=["NORMAL_SERVICE"]
    )
    assert result.status == IdentityStatus.UNVERIFIED_NUMBER
    assert result.risk_contribution == 15

def test_identity_policy_contradiction():
    result = verify_identity(
        phone_number="+919810012345",
        claimed_org_name="CBI",
        detected_labels=["PAYMENT_REQUEST"]
    )
    assert result.status == IdentityStatus.CLAIM_CONTRADICTS_POLICY
    assert result.risk_contribution == 25
    assert "policy violation" in result.explanation.lower()
