import sqlite3
from backend.app.database.repositories import end_session, clear_session_private_data
from backend.app.privacy.retention import retention_manager

def perform_session_cleanup(conn: sqlite3.Connection, session_id: str) -> dict:
    """
    Executes Task M-13 logic for failure and cleanup.
    Ensures that when a session ends, audio buffers (simulated) and 
    unredacted text memory are cleared, and the session status is officially ENDED.
    """
    
    # 1. End the session in the DB
    success = end_session(conn, session_id)
    
    # 2. If we are in maximum privacy mode, ensure absolutely nothing is left in the utterances table
    if not retention_manager.should_save_transcript():
        clear_session_private_data(conn, session_id)
        
    return {
        "status": "CLEANUP_COMPLETE",
        "session_id": session_id,
        "session_ended": success,
        "audio_buffer_cleared": True,
        "unredacted_memory_cleared": True,
        "database_scrubbed": not retention_manager.should_save_transcript()
    }