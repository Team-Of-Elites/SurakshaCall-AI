# Database Module

This module manages the local SQLite database for the SurakshaCall AI backend. It implements the schema, connection management, repository functions, and data seeding scripts.

## Components

### Input
- **Connection requests** from the backend application (typically via FastAPI dependencies or background workers).
- **Domain objects** to persist, such as Session models, Risk snapshots, Evidence events, and Redacted transcripts.

### Output
- `data/suraksha.db`: The SQLite database file created during seeding and modified during runtime.
- **Typed dictionaries/objects** returned from repository functions representing the persisted data.

### Execution & Use
- **Initialization**: Run `python -m backend.app.database.seed` to create the schema, populate trusted organizations, and seed synthetic community patterns.
- **Resetting**: Run `python -m backend.app.database.seed --reset` to drop the existing database and recreate it with default data. This is crucial for returning the system to a clean state for demonstrations.
- **Repositories**: `repositories.py` contains parameterized SQL queries wrapped in Python functions (e.g., `create_session()`, `add_risk_snapshot()`) to be used safely throughout the app without exposing raw SQL strings.
- **Connection**: `connection.py` enforces foreign key constraints at connection time and sets up the row factory to ensure dict-like access to query results.

## Key Principles
- **No Raw Audio Storage**: This schema explicitly does NOT store raw audio files. Audio stays in memory.
- **Redaction First**: Only redacted transcripts should be passed to the repository layer if they are to be stored.
- **Idempotency**: The seed script can be run multiple times safely.
