"""
SurakshaCall AI — Organization Policy Contradiction Checks
Owner: Lakshay
Task: L-08
Determines if caller behaviour violates official published policies of the claimed org.
E.g., CBI demanding money, Bank asking for OTP over phone call.
"""
from typing import List, Optional

POLICY_RULES = {
    "Central Bureau of Investigation": {
        "forbidden_labels": {"PAYMENT_REQUEST", "SECRET_REQUEST", "REMOTE_ACCESS"},
        "description": "CBI officers never demand money transfers, OTPs, or remote app installation over phone calls.",
    },
    "Enforcement Directorate": {
        "forbidden_labels": {"PAYMENT_REQUEST", "SECRET_REQUEST", "REMOTE_ACCESS"},
        "description": "ED officers never request money transfers or credentials over a phone call.",
    },
    "State Bank of India": {
        "forbidden_labels": {"SECRET_REQUEST", "REMOTE_ACCESS", "PAYMENT_REQUEST"},
        "description": "SBI employees never ask for OTP, PIN, CVV, or remote access installation.",
    },
    "HDFC Bank": {
        "forbidden_labels": {"SECRET_REQUEST", "REMOTE_ACCESS", "PAYMENT_REQUEST"},
        "description": "HDFC Bank never requests secret credentials or money transfers via call.",
    },
    "ICICI Bank": {
        "forbidden_labels": {"SECRET_REQUEST", "REMOTE_ACCESS", "PAYMENT_REQUEST"},
        "description": "ICICI Bank never asks for OTPs or remote app installation over phone.",
    },
    "Axis Bank": {
        "forbidden_labels": {"SECRET_REQUEST", "REMOTE_ACCESS", "PAYMENT_REQUEST"},
        "description": "Axis Bank staff never ask customers to share confidential passcodes over phone.",
    },
    "Punjab National Bank": {
        "forbidden_labels": {"SECRET_REQUEST", "REMOTE_ACCESS", "PAYMENT_REQUEST"},
        "description": "PNB staff never request secret codes or app downloads during a call.",
    },
    "Reserve Bank of India": {
        "forbidden_labels": {"PAYMENT_REQUEST", "SECRET_REQUEST"},
        "description": "RBI does not hold individual accounts or demand money transfers from citizens.",
    },
    "TRAI": {
        "forbidden_labels": {"PAYMENT_REQUEST", "SECRET_REQUEST"},
        "description": "TRAI does not call citizens demanding fee payments or security codes.",
    },
}


def check_policy_contradiction(canonical_org: str, detected_labels: List[str]) -> Optional[str]:
    """
    Check if the detected conversation labels violate the published policy of the claimed organization.
    Returns explanation string if policy violated, else None.
    """
    policy = POLICY_RULES.get(canonical_org)
    if not policy:
        return None

    violations = set(detected_labels) & policy["forbidden_labels"]
    if violations:
        violation_names = ", ".join(sorted(violations))
        return f"policy violation: {canonical_org} never requests ({violation_names})"

    return None
