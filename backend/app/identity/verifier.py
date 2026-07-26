"""
SurakshaCall AI — Identity Verifier (Full Implementation)
Owner: Lakshay
Task: L-08

Combines:
  - Phone number normalization (L-09)
  - Trusted directory lookup (seed.json)
  - Alias resolution
  - Policy contradiction check
  - Claim vs reality mismatch detection
"""
import json
import hashlib
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from .phone_numbers import normalize_phone, PhoneInfo
from .aliases import resolve_alias
from .policy_checks import check_policy_contradiction

# Load trusted directory once at startup
_TRUSTED_DIR_PATH = Path(__file__).parent.parent.parent.parent / "data" / "trusted_directory" / "seed.json"

def _load_trusted_directory() -> dict:
    try:
        with open(_TRUSTED_DIR_PATH, encoding="utf-8-sig") as f:
            entries = json.load(f)
        lookup = {}
        for entry in entries:
            lookup[entry["canonical_name"].lower()] = entry
            for alias in entry.get("aliases", []):
                lookup[alias.lower()] = entry
        return lookup
    except Exception:
        return {}

TRUSTED_DIRECTORY = _load_trusted_directory()

# ── Identity Status Codes ───────────────────────────────────────────────────
class IdentityStatus:
    VERIFIED_OFFICIAL        = "VERIFIED_OFFICIAL_NUMBER"
    CLAIM_CONTRADICTS_POLICY = "CLAIM_CONTRADICTS_POLICY"
    UNVERIFIED_NUMBER        = "UNVERIFIED_NUMBER"
    KNOWN_REPORTED_RISK      = "KNOWN_REPORTED_TEST_RISK"
    NOT_IN_DIRECTORY         = "ORGANIZATION_NOT_IN_DIRECTORY"
    INSUFFICIENT_DATA        = "INSUFFICIENT_DATA"


@dataclass
class IdentityResult:
    raw_number: Optional[str]
    phone_info: Optional[PhoneInfo]
    claimed_org: Optional[str]            # What caller claims to be
    canonical_org: Optional[str]          # Resolved canonical name
    status: str                           # IdentityStatus code
    in_trusted_directory: bool
    policy_contradiction: Optional[str]   # Description if violated
    risk_contribution: int                # 0–25 added to Risk Index
    explanation: str                      # Human-readable explanation


def verify_identity(
    phone_number: Optional[str],
    claimed_org_name: Optional[str],
    detected_labels: list[str],
) -> IdentityResult:
    """
    Main identity verification function.
    Called by service.py and by Ron's identity_agent.py.
    """

    # ── Step 1: Phone number normalization ─────────────────────────────────
    phone_info = None
    if phone_number:
        phone_info = normalize_phone(phone_number, source="user_provided")

    # ── Step 2: Resolve claimed org alias ──────────────────────────────────
    canonical_org = None
    if claimed_org_name:
        canonical_org = resolve_alias(claimed_org_name)

    # ── Step 3: Directory lookup ────────────────────────────────────────────
    in_directory = False
    directory_entry = None
    if canonical_org:
        directory_entry = TRUSTED_DIRECTORY.get(canonical_org.lower())
        if not directory_entry and claimed_org_name:
            directory_entry = TRUSTED_DIRECTORY.get(claimed_org_name.lower())
        in_directory = directory_entry is not None

    # ── Step 4: Phone number match against directory ────────────────────────
    number_in_directory = False
    if phone_info and phone_info.e164 and directory_entry:
        official_numbers = directory_entry.get("official_numbers", [])
        national = phone_info.e164.replace("+91", "").strip()
        number_in_directory = any(
            national == n.replace(" ", "") or phone_info.e164.endswith(n.replace(" ", ""))
            for n in official_numbers
        )

    # ── Step 5: Policy contradiction check ─────────────────────────────────
    policy_violation = None
    if canonical_org:
        policy_violation = check_policy_contradiction(canonical_org, detected_labels)

    # ── Step 6: VoIP / suspicious number check ─────────────────────────────
    is_suspicious_number = False
    if phone_info:
        is_suspicious_number = phone_info.is_voip or not phone_info.is_valid

    # ── Step 7: Determine status and risk contribution ─────────────────────
    risk_contribution = 0
    status = IdentityStatus.INSUFFICIENT_DATA
    explanation = "No caller number or organization provided."

    if not phone_number and not claimed_org_name:
        status = IdentityStatus.INSUFFICIENT_DATA
        risk_contribution = 5

    elif policy_violation:
        status = IdentityStatus.CLAIM_CONTRADICTS_POLICY
        risk_contribution = 25
        explanation = (
            f"Caller claims to be '{canonical_org}' but {policy_violation}. "
            f"This directly contradicts the organization's published policy -- high scam indicator."
        )

    elif number_in_directory:
        status = IdentityStatus.VERIFIED_OFFICIAL
        risk_contribution = 0
        explanation = (
            f"Calling number matches a known official number for '{canonical_org}'. "
            f"Likely legitimate -- but stay alert if any credentials are requested."
        )

    elif in_directory and not number_in_directory:
        status = IdentityStatus.UNVERIFIED_NUMBER
        risk_contribution = 15
        explanation = (
            f"Caller claims to be '{canonical_org}' which exists in our directory, "
            f"but the calling number does not match any official numbers. "
            f"Could be spoofed. Do not share credentials."
        )

    elif is_suspicious_number:
        status = IdentityStatus.UNVERIFIED_NUMBER
        risk_contribution = 18
        explanation = (
            "The calling number appears to be a VoIP or unregistered number. "
            "Government and bank employees do not call from VoIP numbers."
        )

    elif claimed_org_name and not in_directory:
        status = IdentityStatus.NOT_IN_DIRECTORY
        risk_contribution = 10
        explanation = (
            f"Caller claims to be '{claimed_org_name}' but this organization "
            f"is not found in our trusted directory. Cannot verify."
        )

    else:
        status = IdentityStatus.UNVERIFIED_NUMBER
        risk_contribution = 8
        explanation = "Number provided but could not be matched to any verified organization."

    return IdentityResult(
        raw_number=phone_number,
        phone_info=phone_info,
        claimed_org=claimed_org_name,
        canonical_org=canonical_org,
        status=status,
        in_trusted_directory=in_directory,
        policy_contradiction=policy_violation,
        risk_contribution=risk_contribution,
        explanation=explanation,
    )
