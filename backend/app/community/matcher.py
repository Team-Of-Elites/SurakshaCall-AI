from typing import Dict, Any, Tuple
from .fingerprint import CampaignFingerprint
from .weights import DEFAULT_WEIGHTS

def jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0

def scalar_similarity(val_a: Any, val_b: Any) -> float:
    if val_a is None or val_b is None:
        return 0.0 # Or neutral policy
    return 1.0 if val_a == val_b else 0.0

class CommunityMatcher:
    def __init__(self, weights: Dict[str, float] = DEFAULT_WEIGHTS):
        self.weights = weights

    def match(self, incoming: CampaignFingerprint, candidate_pattern: dict) -> Tuple[float, Dict[str, float], list]:
        component_scores = {
            "tactics": jaccard_similarity(incoming.tactic_codes, set(candidate_pattern.get("tactic_codes", []))),
            "requested_actions": jaccard_similarity(incoming.requested_action_codes, set(candidate_pattern.get("requested_action_codes", []))),
            "scenario": scalar_similarity(incoming.scenario_code, candidate_pattern.get("scenario_code")),
            "organization_type": scalar_similarity(incoming.organization_type, candidate_pattern.get("organization_type")),
            "threats": jaccard_similarity(incoming.threat_codes, set(candidate_pattern.get("threat_codes", []))),
            "payment_rail": scalar_similarity(incoming.payment_rail, candidate_pattern.get("payment_rail")),
            "channel_switch": scalar_similarity(incoming.channel_switch, candidate_pattern.get("channel_switch")),
            "language_family": scalar_similarity(incoming.language_family, candidate_pattern.get("language_family")),
        }

        similarity = sum(self.weights[k] * component_scores[k] for k in self.weights.keys())
        
        reasons = []
        if component_scores["requested_actions"] > 0.8:
            reasons.append("same requested action")
        if component_scores["scenario"] == 1.0:
            reasons.append("exact scenario match")

        return similarity, component_scores, reasons