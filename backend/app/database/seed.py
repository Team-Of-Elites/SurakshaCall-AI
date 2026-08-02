import sqlite3
import argparse
import json
from pathlib import Path
import sys
import shutil

def run_seed(db_path: str, schema_path: str, seed_dir: str, reset: bool = False):
    db_file = Path(db_path)
    if reset:
        if db_file.exists():
            print(f"Removing {db_file}...")
            db_file.unlink()
        wal_file = Path(f"{db_path}-wal")
        shm_file = Path(f"{db_path}-shm")
        if wal_file.exists(): wal_file.unlink()
        if shm_file.exists(): shm_file.unlink()

    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, isolation_level=None)
    
    try:
        if reset or not db_file.exists():
            print(f"Applying schema from {schema_path}...")
            with open(schema_path, "r") as f:
                conn.executescript(f.read())
        
        print("Inserting seed data (idempotent)...")
        conn.execute("BEGIN IMMEDIATE;")
        try:
            # Reference Sources
            conn.execute("""
                INSERT INTO reference_sources (source_id, source_type, source_title, publisher, first_verified_at_utc, last_verified_at_utc, review_status)
                VALUES (1, 'OFFICIAL_WEBSITE', 'SBI Official Site', 'SBI', '2026-07-28T00:00:00Z', '2026-07-28T00:00:00Z', 'VERIFIED')
                ON CONFLICT(source_id) DO NOTHING
            """)
            
            # Trusted Organizations
            conn.execute("""
                INSERT INTO trusted_organizations (organization_id, canonical_name, organization_type, created_at_utc, updated_at_utc)
                VALUES (1, 'State Bank of India', 'BANK', '2026-07-28T00:00:00Z', '2026-07-28T00:00:00Z')
                ON CONFLICT(canonical_name) DO UPDATE SET active=1
            """)
            
            # Organization Policies
            conn.execute("""
                INSERT INTO organization_policies (organization_id, policy_code, policy_text, severity, verified_at_utc, expires_at_utc, source_id)
                VALUES (1, 'NO_OTP_REQUEST', 'Bank will never ask for OTP', 5, '2026-07-28T00:00:00Z', NULL, 1)
                ON CONFLICT(organization_id, policy_code) DO NOTHING
            """)
            
            # Dev Model Bundle
            conn.execute("""
                INSERT INTO model_bundles (model_bundle_id, asr_model_id, embedding_model_id, classifier_model_id, llm_model_id, rule_set_version, prompt_version, normalizer_version, risk_policy_version, created_at_utc)
                VALUES ('BUNDLE_DEV_UNRESOLVED', 'NOT_SELECTED', 'NOT_SELECTED', 'NOT_SELECTED', 'NOT_SELECTED', 'dev', 'dev', 'dev', 'dev', '2026-07-28T00:00:00Z')
                ON CONFLICT(model_bundle_id) DO NOTHING
            """)
            
            conn.execute("COMMIT;")
            print("Seed complete.")
        except Exception as e:
            conn.execute("ROLLBACK;")
            print(f"Seed failed: {e}")
            raise
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    
    db_path = "data/database/suraksha.db"
    schema_path = "backend/app/database/schema.sql"
    seed_dir = "data/seed/"
    run_seed(db_path, schema_path, seed_dir, args.reset)