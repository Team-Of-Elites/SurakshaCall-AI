# Advance Database Foundation Implementation Documentation

This document tracks every file added or modified to build the full database foundation. The foundation follows a structured, contract-first, standalone-first implementation flow.

## 1. `backend/app/contracts/database_models.py`
### Action
- Added new file.

### Brief Content
Contains Pydantic data models defining the standalone data schemas: `TranscriptFinal`, `DetectionResult`, `RiskDecision`, and `DatabaseHealthEvent`. 

### Knowledge Input
Based on the minimum pipeline contracts described in Phase 1 of `Advanced_Database_Foundation.md`.

### Knowledge Output
Exposes typed domain models independent of FastAPI, WebSockets, or UI types.

### Why
Because the frontend and real backend are not fully ready, the database must define fixed, typed interfaces (contracts) it expects to receive. This ensures that when the rest of the team integrates, they know exactly what data structures to provide.

### Usage
Team members must construct these Pydantic models (or ensure their events match these JSON structures) before calling the persistence layer. The Pydantic validations (e.g., `risk_index` between 0 and 100) prevent bad data from reaching the database.

## 2. \ackend/app/database/schema.sql
### Action
- Modified existing file.
### Brief Content
Contains the full 18-table SQLite schema.
### Knowledge Input
Based on Phase 2 of the Foundation spec. Includes tables for Sessions, Utterances, Evidence, Risk, Identity, Community patterns, and Metrics.
### Knowledge Output
Generates an idempotent database schema.
### Why
Provides the structural backbone for data storage. Overrides the old incomplete schema.
### Usage
Run by connection.py or initialization scripts to create the tables.

## 3. \ackend/app/database/config.py
### Action
- Added new file.
### Brief Content
Defines DatabaseConfig dataclass to hold the database path, timeout, and WAL configuration.
### Knowledge Input
Phase 3 specification.
### Knowledge Output
Configuration settings for the database connection.
### Why
Hardcoding connection settings causes test and production configuration issues. This separates configuration.
### Usage
Imported by connection.py to initialize connections.

## 4. \ackend/app/database/errors.py
### Action
- Added new file.
### Brief Content
Defines a specific hierarchy of exceptions (DatabaseError, DatabaseUnavailableError, etc.).
### Knowledge Input
Phase 3 specification for safe error handling.
### Knowledge Output
Safe, user-facing error types instead of raw SQL errors.
### Why
Never expose raw SQL strings or private data in API errors. The backend translates these into clean HTTP responses.
### Usage
Raised by repositories when a database constraint fails or the DB is locked.

## 5. \ackend/app/database/connection.py
### Action
- Modified existing file.
### Brief Content
Provides open_connection and 	ransaction context managers. Enforces foreign keys, WAL, and strict timeouts.
### Knowledge Input
Phase 3 of the Foundation spec.
### Knowledge Output
A safe sqlite3.Connection object ready for repository use.
### Why
Ensures that all connections universally enforce data integrity and that transactions use BEGIN IMMEDIATE for SQLite concurrency safety.
### Usage
Wrap repository access or service execution with with open_connection(config) as conn:.

## 6. \ackend/app/database/health.py
### Action
- Added new file.
### Brief Content
Performs a health check of the SQLite database returning standard operational metrics like status (AVAILABLE or UNAVAILABLE), journal_mode, and foreign keys configuration.
### Knowledge Input
Phase 3 requirements for safe UI reporting.
### Knowledge Output
HealthCheckResult dataclass to expose state safely.
### Why
Instead of failing mysteriously, the backend will report health degradation cleanly without breaking active memory safety.
### Usage
Called by backend health-check endpoints.

## 7. \ackend/app/database/repositories.py
### Action
- Modified existing file.
### Brief Content
Organized SQL queries into 9 distinct repository classes: SessionRepository, UtteranceRepository, EvidenceRepository, RiskRepository, IdentityRepository, CommunityRepository, ModelRepository, FeedbackRepository, EvaluationRepository.
### Knowledge Input
Phase 4 of the Foundation architecture.
### Knowledge Output
Abstracts SQLite operations into Python objects mapping strictly to our DB tables.
### Why
Directly writing SQL inside backend APIs/agents creates tightly coupled, messy code. These repositories enforce schema shapes.
### Usage
Instantiate SessionRepository(conn) and call methods like create_session().

## 8. \ackend/app/database/services.py
### Action
- Added new file.
### Brief Content
Implements persist_decision_bundle logic.
### Knowledge Input
Phase 3 transaction requirements.
### Knowledge Output
Ensures cross-repository operations happen in a single, safe 	ransaction().
### Why
If inserting an evidence event succeeds but risk snapshot fails, the DB reaches an invalid state. Services bundle them into single operations.
### Usage
Called by backend orchestration to save full decision states simultaneously.

## 9. \ackend/app/database/seed.py
### Action
- Modified existing file.
### Brief Content
Implements the idempotent seed logic and a reset flag to wipe and rebuild the database safely.
### Knowledge Input
Phase 5 (Seed and Reset).
### Knowledge Output
Creates reliable test data for Trusted Organizations, aliases, official numbers, policies, and community patterns without leaking real private data.
### Why
We need safe mock data to test the system since the frontend isn't ready. This ensures the DB can always be built into a known good state.
### Usage
Run python -m app.database.seed to insert data idempotently or --reset to wipe and recreate it.

## 10. \ackend/app/privacy/redaction.py
### Action
- Added new file.
### Brief Content
Uses RegEx to replace emails, UPIs, URLs, PAN, Aadhaar, OTPs, and Card numbers with [REDACTED] tags.
### Knowledge Input
Phase 6 (Privacy Engine).
### Knowledge Output
A function 
edact_sensitive_text(raw_text) that enforces the redaction order before any database write.
### Why
SurakshaCall must never persist plain-text user secrets. Redaction happens at the persistence boundary.
### Usage
Called by the backend orchestrator before saving utterances to UtteranceRepository.

## 11. \ackend/app/privacy/retention.py
### Action
- Added new file.
### Brief Content
Defines RetentionPolicy class which dictates that in MAXIMUM_PRIVACY mode, should_persist_utterance returns False.
### Knowledge Input
Phase 6 (Privacy Engine).
### Knowledge Output
Determines what is allowed to be saved based on the active session's privacy mode.
### Why
Raw or redacted transcripts must not be stored in MAXIMUM_PRIVACY.
### Usage
Repositories and services call this before deciding to run INSERT statements.

## 12. \ackend/app/privacy/validators.py
### Action
- Added new file.
### Brief Content
Provides alidate_safe_for_persistence to raise a PrivacyViolationError if forbidden keys like 
aw_audio or 
aw_text are attempted to be written.
### Knowledge Input
Phase 6 (Privacy Engine).
### Knowledge Output
Last line of defense against privacy leakage.
### Why
Developers might accidentally try to log or persist raw fields. This explicit validator stops it.
### Usage
Called before executing final payload inserts.

## 13. \ackend/app/community/fingerprint.py
### Action
- Added new file.
### Brief Content
Defines CampaignFingerprint which holds the structured categorization of a scam attempt (tactic codes, requested actions, threats).
### Knowledge Input
Phase 8 (Community Intelligence).
### Knowledge Output
A privacy-safe payload used for community intelligence matching.
### Why
Raw audio or transcripts cannot be used to search community databases. The fingerprint extracts only high-level categorizations to ensure privacy.
### Usage
Generated by the AI rule-engine and passed into CommunityMatcher.

## 14. \ackend/app/community/weights.py
### Action
- Added new file.
### Brief Content
Stores DEFAULT_WEIGHTS dict mapping features (like tactics, requested_actions) to their respective fractional weights (must sum to 1.0).
### Knowledge Input
Phase 8 (Community Intelligence).
### Knowledge Output
Centralized tuning mechanism for similarity matching.
### Why
Scoring logic shouldn't be scattered. Defining weights in one place allows easy adjustments when we calibrate the fraud models.
### Usage
Imported by matcher.py for Weighted Jaccard calculations.

## 15. \ackend/app/community/matcher.py
### Action
- Added new file.
### Brief Content
Implements Weighted Jaccard similarity for sets and scalar comparisons for strings. Calculates overall similarity score between an incoming fingerprint and known database patterns.
### Knowledge Input
Phase 8 calculations.
### Knowledge Output
Produces (similarity_score, component_scores, match_reasons).
### Why
We do not use ChromaDB or Vector DBs for this structured task. This logic is fast, explainable, and deterministic.
### Usage
Called by the community service to determine if an incoming call closely matches a known community threat campaign.

## 16. \ackend/app/database/cleanup.py
### Action
- Added new file.
### Brief Content
Implements perform_end_session_cleanup. Deletes prohibited utterances from the database for MAXIMUM_PRIVACY sessions while maintaining evidence and risk summaries. Returns a structured JSON summary.
### Knowledge Input
Phase 10 (Cleanup and Retention Enforcement).
### Knowledge Output
Privacy audit trail.
### Why
Automatically triggered at the end of a session, this guarantees that we actively strip data out to meet our strict privacy claims. 
### Usage
Called by the backend when a WebSocket session ends.

## 17. \ackend/app/database/backup.py
### Action
- Added new file.
### Brief Content
Uses the official sqlite3 ackup() API to create consistent snapshots of the database into data/backups/. Runs PRAGMA integrity_check on the resulting file and outputs a JSON manifest.
### Knowledge Input
Phase 11 (Backup, Restore, and Corruption Safety).
### Knowledge Output
Produces safely restorable database files without stopping active reads/writes.
### Why
Blindly copying a live SQLite file (.db while .wal is active) causes corruption. The API handles this safely.
### Usage
Run by scheduled background tasks or manually via a CLI script to dump the DB safely.

## 18. scripts/init_database.py
### Action
- Added new file.
### Brief Content
CLI script calling 
un_seed(reset=False).
### Knowledge Input
Phase 12 Mock/Init scripts.
### Knowledge Output
Safe wrapper to bootstrap the database if it doesn't exist.
### Why
Useful for onboarding new developers.
### Usage
Run python scripts/init_database.py to get started.

## 19. scripts/reset_database.py
### Action
- Added new file.
### Brief Content
CLI script calling 
un_seed(reset=True).
### Knowledge Input
Phase 12 scripts.
### Knowledge Output
Wipes everything and recreates the DB structure.
### Why
During testing, state gets polluted. This offers a deterministic fresh start.
### Usage
Run python scripts/reset_database.py.

## 20. scripts/run_mock_database_pipeline.py
### Action
- Added new file.
### Brief Content
Simulates a full mock integration vertical slice: initializing DB -> starting session -> saving redacted utterances -> calling cleanup -> verifying zero footprint logic.
### Knowledge Input
Phase 12 (Mock Vertical Slice).
### Knowledge Output
Proofs that the DB repositories and privacy engine work independently from the unbuilt frontend and backend.
### Why
Mayank needs to prove his component's contract is solid now, without being blocked by Ron and Palak.
### Usage
Run python scripts/run_mock_database_pipeline.py. It should print Maximum privacy cleanup: PASS.

## 21. scripts/export_evaluation.py
### Action
- Added new file.
### Brief Content
CLI script to invoke export_evaluation_csv() from the EvaluationRepository. Takes an --run-id and --out path as arguments.
### Knowledge Input
Phase 9 / 15.6 (CSV Export).
### Knowledge Output
Generates the specific 16-column CSV report of an evaluation run.
### Why
Needed for QA teams to review the accuracy metrics (e.g. correct_evidence_count, ctual_max_risk) outside the database.
### Usage
Run python scripts/export_evaluation.py --run-id RUN_001 --out data/evaluation/exports/run1.csv.

## 22. scripts/submit_feedback.py
### Action
- Added new file.
### Brief Content
CLI script to insert user_feedback using FeedbackRepository. Allows flags like --session, --type, and --comment.
### Knowledge Input
Phase 9 / 15.7 (User feedback without frontend).
### Knowledge Output
Persists user reviews (e.g., FALSE_POSITIVE) linked to a session ID.
### Why
Since the frontend isn't complete, this allows immediate feedback collection for evaluation runs, giving developers a way to flag false positives quickly.
### Usage
Run python scripts/submit_feedback.py --session S001 --type FALSE_POSITIVE --comment "Legitimate test scenario".
