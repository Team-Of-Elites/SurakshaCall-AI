import sqlite3
import os
from typing import Generator
from pathlib import Path

# Base directory setup for data
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "suraksha.db"

def get_connection() -> sqlite3.Connection:
    """
    Creates and returns a connection to the SQLite database.
    Ensures that foreign keys are enabled (PRAGMA foreign_keys = ON).
    Returns rows as sqlite3.Row for dict-like access.
    """
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    
    return conn

def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Dependency generator for FastAPI (if needed in the future).
    Yields a database connection and ensures it is closed after use.
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()