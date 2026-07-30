import argparse
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.database.config import DatabaseConfig
from backend.app.database.connection import open_connection
from backend.app.database.repositories import FeedbackRepository

def main():
    parser = argparse.ArgumentParser(description="Submit user feedback.")
    parser.add_argument("--session", required=True, help="The session ID")
    parser.add_argument("--type", required=True, choices=["CORRECT_WARNING", "FALSE_POSITIVE", "FALSE_NEGATIVE", "INCORRECT_REASON", "OTHER"])
    parser.add_argument("--comment", required=False, default="")
    args = parser.parse_args()

    config = DatabaseConfig(path=Path("data/database/suraksha.db"))

    with open_connection(config) as conn:
        repo = FeedbackRepository(conn)
        feedback_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        
        try:
            repo.save_user_feedback(
                feedback_id=feedback_id,
                session_id=args.session,
                feedback_type=args.type,
                source="EVALUATION",
                created_at_utc=created_at,
                comment_redacted=args.comment
            )
            print(f"Feedback {feedback_id} submitted successfully.")
        except Exception as e:
            print(f"Failed to submit feedback: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
