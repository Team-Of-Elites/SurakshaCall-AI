import sqlite3
import json
from typing import Optional, Dict, Any
from backend.app.community.fingerprint import CommunityFingerprint
from backend.app.community.matcher import calculate_similarity

def get_all_community_patterns(conn: sqlite3.Connection) -> list[CommunityFingerprint]:
    """Retrieves all seeded community patterns from the database."""
    cursor = conn.execute("SELECT * FROM community_patterns")
    patterns = []
    
    for row in cursor.fetchall():
        tactics_list = json.loads(row["tactics"])
        pattern = CommunityFingerprint(
            id=row["id"],
            schema_version=row["schema_version"],
            tactics=tactics_list,
            organization_type=row["organization_type"],
            scenario=row["scenario"],
            requested_action=row["requested_action"],
            threat_type=row["threat_type"],
            channel_switch=row["channel_switch"],
            language_family=row["language_family"]
        )
        patterns.append(pattern)
        
    return patterns

def evaluate_community_risk(conn: sqlite3.Connection, live_fingerprint_data: dict) -> Optional[Dict[str, Any]]:
    """
    Takes a raw dict representing the live call's fingerprint, converts it to the model,
    compares it against all known DB patterns, and returns the highest matching result 
    if it exceeds a reasonable threshold (e.g., > 0.5 similarity).
    """
    try:
        live_pattern = CommunityFingerprint(**live_fingerprint_data)
    except Exception as e:
        print(f"Invalid live fingerprint data: {e}")
        return None

    db_patterns = get_all_community_patterns(conn)
    
    best_match = None
    highest_score = 0.0
    
    for db_pattern in db_patterns:
        match_result = calculate_similarity(live_pattern, db_pattern)
        if match_result["similarity"] > highest_score:
            highest_score = match_result["similarity"]
            best_match = match_result
            
    # Return the best match only if there is a meaningful similarity
    if highest_score >= 0.5:
        return best_match
        
    return None