# Weights for the Weighted Jaccard Similarity Algorithm
# These define how important each field is when determining if a live call
# matches a historical community fraud pattern.

SIMILARITY_WEIGHTS = {
    "requested_action": 4.0,  # Most critical: e.g., asking for an OTP or money transfer
    "tactics": 3.0,           # e.g., Authority + Urgency
    "scenario": 3.0,          # e.g., DIGITAL_ARREST or BANK_KYC
    "threat_type": 2.0,       # e.g., LOSS_OF_FUNDS
    "organization_type": 2.0, # e.g., BANK vs LAW_ENFORCEMENT
    "channel_switch": 1.0,    # e.g., switching to WhatsApp or Video Call
    "language_family": 1.0    # e.g., HI_EN (Hindi-English mix)
}

def get_total_weight() -> float:
    return sum(SIMILARITY_WEIGHTS.values())