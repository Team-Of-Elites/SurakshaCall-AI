import sqlite3
from pathlib import Path
from datetime import datetime
import json
from .connection import DatabaseConfig

def perform_backup(config: DatabaseConfig, backup_dir: str = "data/backups") -> str:
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(backup_dir) / f"suraksha_demo_{timestamp}.db"
    
    # Connect to live database
    live_conn = sqlite3.connect(config.path)
    
    # Connect to backup file
    backup_conn = sqlite3.connect(backup_path)
    
    try:
        # Perform safe SQLite backup API call
        live_conn.backup(backup_conn)
        
        # Verify integrity of the backup
        cur = backup_conn.execute("PRAGMA integrity_check;")
        result = cur.fetchone()[0]
        if result != "ok":
            raise sqlite3.DatabaseError(f"Backup corrupted: {result}")
            
        manifest = {
            "backup_version": "1.0",
            "source": str(config.path),
            "destination": str(backup_path),
            "timestamp": timestamp,
            "contains_raw_audio": False # Hard rule: raw audio never inside DB
        }
        
        manifest_path = Path(backup_dir) / f"suraksha_demo_{timestamp}_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
            
        return str(backup_path)
    finally:
        live_conn.close()
        backup_conn.close()
