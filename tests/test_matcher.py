import pytest
from backend.app.community.fingerprint import CommunityFingerprint
from backend.app.community.matcher import calculate_similarity

def test_identical_fingerprints():
    fp1 = CommunityFingerprint(
        schema_version=1,
        tactics=["AUTHORITY", "URGENCY"],
        organization_type="BANK",
        scenario="BANK_KYC",
        requested_action="SECRET_CODE",
        threat_type="ACCOUNT_FREEZE",
        channel_switch="NONE",
        language_family="HI_EN"
    )
    
    # Matching against itself should yield a 1.0 (100%) score
    result = calculate_similarity(fp1, fp1)
    assert result["similarity"] == 1.0
    assert len(result["match_reasons"]) == 7 # All 7 fields should match

def test_partial_fingerprint_match():
    live_fp = CommunityFingerprint(
        schema_version=1,
        tactics=["AUTHORITY", "URGENCY", "SYMPATHY"],
        organization_type="BANK",
        scenario="BANK_KYC",
        requested_action="SECRET_CODE", # 4 points
        threat_type="ACCOUNT_FREEZE",   # 2 points
        channel_switch="WHATSAPP",      # Mismatch (0 points)
        language_family="EN"            # Mismatch (0 points)
    )
    
    db_fp = CommunityFingerprint(
        schema_version=1,
        tactics=["AUTHORITY", "URGENCY"],
        organization_type="POLICE",     # Mismatch (0 points)
        scenario="DIGITAL_ARREST",      # Mismatch (0 points)
        requested_action="SECRET_CODE", # 4 points
        threat_type="ACCOUNT_FREEZE",   # 2 points
        channel_switch="NONE",
        language_family="HI_EN"
    )
    
    result = calculate_similarity(live_fp, db_fp)
    # The score should be > 0.0 but < 1.0
    assert 0.0 < result["similarity"] < 1.0
    assert "same requested action (SECRET_CODE)" in result["match_reasons"]
    assert "same threat type (ACCOUNT_FREEZE)" in result["match_reasons"]
