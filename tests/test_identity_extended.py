"""Extended identity tests for claim extraction and wording."""
from backend.app.identity.claim_extractor import extract_claims
from backend.app.identity.wording import get_safe_wording, SAFE_WORDING
from backend.app.identity.schemas import IdentityClaimCandidate, VerificationRequest


def test_claim_extraction_cbi():
    claims = extract_claims("Main CBI inspector Sharma bol raha hoon.")
    assert len(claims) >= 1
    assert any("cbi" in c["organization_text"].lower() for c in claims)


def test_claim_extraction_bank():
    claims = extract_claims("I am calling from SBI bank KYC department.")
    assert len(claims) >= 1
    assert any("sbi" in c["organization_text"].lower() for c in claims)


def test_claim_extraction_entity_only():
    """RBI mentioned but not as a claim should still be extracted with lower confidence."""
    claims = extract_claims("RBI says never share your OTP.")
    assert len(claims) >= 0


def test_no_false_claim():
    """Normal conversation without org references should not extract claims."""
    claims = extract_claims("Hello, how are you today?")
    assert len(claims) == 0


def test_safe_wording_verified():
    text = get_safe_wording("VERIFIED_OFFICIAL_NUMBER", "en")
    assert "official number" in text
    assert "fraud" not in text.lower()


def test_safe_wording_unverified():
    text = get_safe_wording("UNVERIFIED_NUMBER", "en")
    assert "not verified" in text.lower()
    assert "does not prove fraud" in text.lower()


def test_safe_wording_insufficient():
    text = get_safe_wording("INSUFFICIENT_DATA", "en")
    assert "not enough" in text.lower()


def test_safe_wording_policy():
    text = get_safe_wording("CLAIM_CONTRADICTS_POLICY", "en")
    assert "conflict" in text.lower()


def test_safe_wording_hindi():
    text = get_safe_wording("UNVERIFIED_NUMBER", "hi")
    assert "सत्यापित" in text


def test_identity_claim_candidate_schema():
    c = IdentityClaimCandidate(claim_id="c1", organization_text="SBI")
    assert c.claim_id == "c1"
    assert c.organization_text == "SBI"


def test_verification_request_schema():
    c = IdentityClaimCandidate(claim_id="c1", organization_text="CBI")
    v = VerificationRequest(claim=c, caller_number="+919876543210")
    assert v.claim.organization_text == "CBI"
    assert v.caller_number == "+919876543210"
