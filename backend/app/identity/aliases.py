"""
SurakshaCall AI — Organization Alias Resolver
Owner: Lakshay
Task: L-08
Maps variations of org names ("sbi", "state bank") to canonical directory names.
"""

ALIAS_MAP = {
    # Banks
    "sbi": "State Bank of India",
    "state bank": "State Bank of India",
    "state bank of india": "State Bank of India",
    "hdfc": "HDFC Bank",
    "hdfc bank": "HDFC Bank",
    "icici": "ICICI Bank",
    "icici bank": "ICICI Bank",
    "axis": "Axis Bank",
    "axis bank": "Axis Bank",
    "pnb": "Punjab National Bank",
    "punjab national bank": "Punjab National Bank",
    "kotak": "Kotak Mahindra Bank",
    "kotak bank": "Kotak Mahindra Bank",

    # Law enforcement & Authorities
    "cbi": "Central Bureau of Investigation",
    "central bureau": "Central Bureau of Investigation",
    "ed": "Enforcement Directorate",
    "enforcement directorate": "Enforcement Directorate",
    "rbi": "Reserve Bank of India",
    "reserve bank": "Reserve Bank of India",
    "cyber crime": "Cyber Crime Department",
    "cybercell": "Cyber Crime Department",
    "cyber cell": "Cyber Crime Department",
    "police": "Police Department",
    "trai": "TRAI",
    "telecom regulatory": "TRAI",
}


def resolve_alias(claimed_name: str) -> str:
    """
    Resolve an informal or raw org name to its canonical directory entry name.
    """
    key = claimed_name.lower().strip()
    return ALIAS_MAP.get(key, claimed_name)
