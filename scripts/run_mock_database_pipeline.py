import sys
from pathlib import Path
from datetime import datetime, timezone
import uuid

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.database.config import DatabaseConfig
from backend.app.database.connection import open_connection
from backend.app.database.repositories import SessionRepository, UtteranceRepository
from backend.app.database.seed import run_seed
from backend.app.database.cleanup import perform_end_session_cleanup

def run():
    print("Initializing mock vertical slice...")
    db_path = "data/database/suraksha_mock.db"
    schema_path = "backend/app/database/schema.sql"
    seed_dir = "data/seed/"
    run_seed(db_path, schema_path, seed_dir, reset=True)
    
    config = DatabaseConfig(path=Path(db_path))
    session_id = "MOCK-SESSION-001"
    
    with open_connection(config) as conn:
        print("1. Creating session...")
        session_repo = SessionRepository(conn)
        now = datetime.now(timezone.utc).isoformat()
        session_repo.create_session(
            session_id=session_id,
            input_mode="MOCK",
            privacy_mode="MAXIMUM_PRIVACY",
            config_version="v1.0",
            created_at_utc=now
        )
        
        print("2. Storing mock redacted utterance...")
        utterance_repo = UtteranceRepository(conn)
        utterance_repo.add_redacted_utterance(
            utterance_id=str(uuid.uuid4()),
            session_id=session_id,
            sequence=1,
            speaker_role="CALLER",
            started_ms=0,
            ended_ms=2000,
            redacted_text="My OTP is [OTP_PIN_REDACTED]",
            asr_model_id="whisper-mock",
            created_at_utc=now
        )
        
        print("3. Validating max privacy deletion due to session end...")
        result = perform_end_session_cleanup(conn, session_id, privacy_mode="MAXIMUM_PRIVACY")
        
        utterances_left = utterance_repo.count_session_utterances(session_id)
        if utterances_left == 0 and result["utterances_deleted"] > 0:
            print("Maximum privacy cleanup: PASS")
        else:
            print("Maximum privacy cleanup: FAIL")
            
        print("Mock execution complete.")

if __name__ == "__main__":
    run()
