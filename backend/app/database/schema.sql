-- SurakshaCall AI SQLite Database Schema
-- Ensures foreign keys are enabled at the connection level before executing.

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    input_mode TEXT NOT NULL,
    caller_number_redacted TEXT,
    transcript_retention_enabled INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS utterances (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    speaker TEXT NOT NULL,
    text_redacted TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evidence_events (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS risk_snapshots (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    risk_score REAL NOT NULL,
    risk_level TEXT NOT NULL,
    explanation TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trusted_organizations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS official_numbers (
    number TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES trusted_organizations (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS verification_results (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    status TEXT NOT NULL,
    organization_id TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES trusted_organizations (id)
);

CREATE TABLE IF NOT EXISTS community_patterns (
    id TEXT PRIMARY KEY,
    schema_version INTEGER NOT NULL DEFAULT 1,
    tactics TEXT NOT NULL, -- Stored as JSON string
    organization_type TEXT NOT NULL,
    scenario TEXT NOT NULL,
    requested_action TEXT NOT NULL,
    threat_type TEXT NOT NULL,
    channel_switch TEXT NOT NULL,
    language_family TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS community_matches (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    matched_pattern_id TEXT NOT NULL,
    similarity REAL NOT NULL,
    campaign_label TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (matched_pattern_id) REFERENCES community_patterns (id)
);

CREATE TABLE IF NOT EXISTS system_metrics (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evaluation_runs (
    id TEXT PRIMARY KEY,
    run_date TEXT NOT NULL,
    metrics_summary TEXT NOT NULL -- Stored as JSON string
);