import sqlite3
import datetime
from typing import Optional, Dict, Any, List

def _get_utc_now_str() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def create_session(conn: sqlite3.Connection, session_id: str, input_mode: str, caller_number_redacted: Optional[str] = None) -> Dict[str, Any]:
    """Creates a new session record in the database."""
    started_at = _get_utc_now_str()
    status = "ACTIVE"
    
    conn.execute("""
        INSERT INTO sessions (id, started_at, input_mode, caller_number_redacted, status)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, started_at, input_mode, caller_number_redacted, status))
    conn.commit()
    
    return {
        "id": session_id,
        "started_at": started_at,
        "input_mode": input_mode,
        "caller_number_redacted": caller_number_redacted,
        "status": status
    }

def get_session(conn: sqlite3.Connection, session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a session by its ID."""
    cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    
    if row:
        return dict(row)
    return None

def end_session(conn: sqlite3.Connection, session_id: str) -> bool:
    """Marks a session as ended."""
    ended_at = _get_utc_now_str()
    
    cursor = conn.execute("""
        UPDATE sessions
        SET status = 'ENDED', ended_at = ?
        WHERE id = ? AND status = 'ACTIVE'
    """, (ended_at, session_id))
    conn.commit()
    
    return cursor.rowcount > 0

def add_risk_snapshot(conn: sqlite3.Connection, snapshot_id: str, session_id: str, risk_score: float, risk_level: str, explanation: str) -> Dict[str, Any]:
    """Adds a new risk snapshot for a session."""
    timestamp = _get_utc_now_str()
    
    conn.execute("""
        INSERT INTO risk_snapshots (id, session_id, risk_score, risk_level, explanation, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (snapshot_id, session_id, risk_score, risk_level, explanation, timestamp))
    conn.commit()
    
    return {
        "id": snapshot_id,
        "session_id": session_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "explanation": explanation,
        "timestamp": timestamp
    }

def add_redacted_utterance(conn: sqlite3.Connection, utterance_id: str, session_id: str, speaker: str, text_redacted: str) -> None:
    timestamp = _get_utc_now_str()
    conn.execute("""
        INSERT INTO utterances (id, session_id, speaker, text_redacted, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (utterance_id, session_id, speaker, text_redacted, timestamp))
    conn.commit()

def add_evidence_event(conn: sqlite3.Connection, event_id: str, session_id: str, category: str, description: str) -> None:
    timestamp = _get_utc_now_str()
    conn.execute("""
        INSERT INTO evidence_events (id, session_id, category, description, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (event_id, session_id, category, description, timestamp))
    conn.commit()

def find_organization_by_alias(conn: sqlite3.Connection, alias: str) -> Optional[Dict[str, Any]]:
    # In a real app this might use fuzzy matching. For this prototype, exact match or simple LIKE.
    cursor = conn.execute("SELECT * FROM trusted_organizations WHERE name LIKE ?", (f"%{alias}%",))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None

def find_official_number(conn: sqlite3.Connection, number: str) -> Optional[Dict[str, Any]]:
    cursor = conn.execute("SELECT * FROM official_numbers WHERE number = ?", (number,))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None

def add_verification_result(conn: sqlite3.Connection, result_id: str, session_id: str, status: str, organization_id: Optional[str] = None) -> None:
    timestamp = _get_utc_now_str()
    conn.execute("""
        INSERT INTO verification_results (id, session_id, status, organization_id, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (result_id, session_id, status, organization_id, timestamp))
    conn.commit()

def add_community_match(conn: sqlite3.Connection, match_id: str, session_id: str, matched_pattern_id: str, similarity: float, campaign_label: str) -> None:
    timestamp = _get_utc_now_str()
    conn.execute("""
        INSERT INTO community_matches (id, session_id, matched_pattern_id, similarity, campaign_label, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (match_id, session_id, matched_pattern_id, similarity, campaign_label, timestamp))
    conn.commit()

def save_metric(conn: sqlite3.Connection, metric_id: str, session_id: str, metric_name: str, metric_value: float) -> None:
    timestamp = _get_utc_now_str()
    conn.execute("""
        INSERT INTO system_metrics (id, session_id, metric_name, metric_value, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (metric_id, session_id, metric_name, metric_value, timestamp))
    conn.commit()

def clear_session_private_data(conn: sqlite3.Connection, session_id: str) -> None:
    # Double-check that all utterances are removed (even though they are theoretically redacted, privacy requires active clearing)
    conn.execute("DELETE FROM utterances WHERE session_id = ?", (session_id,))
    conn.commit()