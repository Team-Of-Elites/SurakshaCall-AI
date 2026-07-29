import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.database.seed import run_seed

if __name__ == "__main__":
    print("Warning: This will destroy the existing database.")
    db_path = "data/database/suraksha.db"
    schema_path = "backend/app/database/schema.sql"
    seed_dir = "data/seed/"
    run_seed(db_path, schema_path, seed_dir, reset=True)
    print("Database reset successfully.")
