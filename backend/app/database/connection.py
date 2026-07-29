from contextlib import contextmanager
import sqlite3
from .config import DatabaseConfig

@contextmanager
def open_connection(config: DatabaseConfig):
    config.path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        config.path,
        timeout=config.busy_timeout_ms / 1000,
        isolation_level=None,
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row

    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(f"PRAGMA busy_timeout = {config.busy_timeout_ms};")
        conn.execute(f"PRAGMA synchronous = {config.synchronous};")
        conn.execute("PRAGMA temp_store = MEMORY;")

        if config.enable_wal and str(config.path) != ":memory:":
            conn.execute("PRAGMA journal_mode = WAL;")

        yield conn
    finally:
        conn.close()

@contextmanager
def transaction(conn: sqlite3.Connection):
    try:
        conn.execute("BEGIN IMMEDIATE;")
        yield conn
        conn.execute("COMMIT;")
    except Exception:
        conn.execute("ROLLBACK;")
        raise