import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.database.config import DatabaseConfig
from backend.app.database.connection import open_connection
from backend.app.database.repositories import EvaluationRepository

def main():
    parser = argparse.ArgumentParser(description="Export evaluation runs to CSV.")
    parser.add_argument("--run-id", required=True, help="The evaluation_run_id to export")
    parser.add_argument("--out", required=True, help="Output CSV path")
    args = parser.parse_args()

    config = DatabaseConfig(path=Path("data/database/suraksha.db"))

    with open_connection(config) as conn:
        repo = EvaluationRepository(conn)
        try:
            repo.export_evaluation_csv(args.run_id, args.out)
            print(f"Successfully exported run {args.run_id} to {args.out}")
        except Exception as e:
            print(f"Error exporting evaluation run: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
