import pytest
import sqlite3
import os
from backend.app.database.repositories import create_session, get_session, end_session

# Load the schema path safely
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app', 'database', 'schema.sql')

@pytest.fixture
def test_db():
    """Sets up a clean in-memory SQLite database for testing."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # Load and execute the schema
    with open(SCHEMA_PATH, 'r') as f:
        schema_script = f.read()
    conn.executescript(schema_script)
    
    yield conn
    conn.close()

def test_session_lifecycle(test_db):
    session_id = "test_session_001"
    
    # 1. Create a session
    created = create_session(test_db, session_id, input_mode="AUDIO")
    assert created["id"] == session_id
    assert created["status"] == "ACTIVE"
    
    # 2. Retrieve the session
    retrieved = get_session(test_db, session_id)
    assert retrieved is not None
    assert retrieved["id"] == session_id
    assert retrieved["status"] == "ACTIVE"
    
    # 3. End the session
    success = end_session(test_db, session_id)
    assert success is True
    
    # 4. Verify it is marked ENDED
    retrieved_ended = get_session(test_db, session_id)
    assert retrieved_ended["status"] == "ENDED"
    assert retrieved_ended["ended_at"] is not None
