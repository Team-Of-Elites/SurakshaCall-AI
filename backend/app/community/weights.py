DEFAULT_WEIGHTS = {
    "tactics": 0.25,
    "requested_actions": 0.25,
    "scenario": 0.15,
    "organization_type": 0.10,
    "threats": 0.10,
    "payment_rail": 0.05,
    "channel_switch": 0.05,
    "language_family": 0.05,
}

def validate_weights():
    if not (0.99 <= sum(DEFAULT_WEIGHTS.values()) <= 1.01):
        raise ValueError("Community weights must sum to 1.0")

validate_weights()