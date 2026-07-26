from typing import Dict, Any
from backend.app.community.fingerprint import CommunityFingerprint
from backend.app.community.weights import SIMILARITY_WEIGHTS, get_total_weight

def calculate_similarity(live_pattern: CommunityFingerprint, db_pattern: CommunityFingerprint) -> Dict[str, Any]:
    """
    Calculates the Weighted Jaccard Similarity between a live call's fingerprint
    and a known historical community pattern from the database.
    
    Returns a dictionary containing the similarity score (0.0 to 1.0) and match reasons.
    """
    score = 0.0
    total_weight = get_total_weight()
    match_reasons = []

    # 1. Requested Action Match (Highest Weight)
    if live_pattern.requested_action == db_pattern.requested_action:
        score += SIMILARITY_WEIGHTS["requested_action"]
        match_reasons.append(f"same requested action ({live_pattern.requested_action})")

    # 2. Scenario Match
    if live_pattern.scenario == db_pattern.scenario:
        score += SIMILARITY_WEIGHTS["scenario"]
        match_reasons.append(f"same scenario ({live_pattern.scenario})")

    # 3. Tactics Match (List intersection)
    live_tactics = set(live_pattern.tactics)
    db_tactics = set(db_pattern.tactics)
    if live_tactics and db_tactics:
        intersection = live_tactics.intersection(db_tactics)
        union = live_tactics.union(db_tactics)
        # Partial points based on Jaccard similarity of tactics list multiplied by tactics weight
        tactics_score = (len(intersection) / len(union)) * SIMILARITY_WEIGHTS["tactics"]
        score += tactics_score
        if tactics_score > 0:
            match_reasons.append(f"tactics overlap ({', '.join(intersection)})")

    # 4. Threat Type Match
    if live_pattern.threat_type == db_pattern.threat_type:
        score += SIMILARITY_WEIGHTS["threat_type"]
        match_reasons.append(f"same threat type ({live_pattern.threat_type})")

    # 5. Organization Type Match
    if live_pattern.organization_type == db_pattern.organization_type:
        score += SIMILARITY_WEIGHTS["organization_type"]
        match_reasons.append(f"same organization type ({live_pattern.organization_type})")

    # 6. Channel Switch Match
    if live_pattern.channel_switch == db_pattern.channel_switch:
        score += SIMILARITY_WEIGHTS["channel_switch"]
        match_reasons.append(f"same channel switch ({live_pattern.channel_switch})")

    # 7. Language Family Match
    if live_pattern.language_family == db_pattern.language_family:
        score += SIMILARITY_WEIGHTS["language_family"]
        match_reasons.append(f"same language family ({live_pattern.language_family})")

    # Final normalized score
    normalized_score = score / total_weight

    return {
        "matched_pattern_id": db_pattern.id,
        "similarity": round(normalized_score, 4),
        "campaign_label": db_pattern.scenario,
        "match_reasons": match_reasons,
        "data_source": "synthetic_prototype_patterns"
    }