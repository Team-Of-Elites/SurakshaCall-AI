PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;
PRAGMA temp_store = MEMORY;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    checksum TEXT NOT NULL,
    applied_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS model_bundles (
    model_bundle_id TEXT PRIMARY KEY,
    asr_model_id TEXT NOT NULL,
    embedding_model_id TEXT NOT NULL,
    classifier_model_id TEXT NOT NULL,
    llm_model_id TEXT,
    rule_set_version TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    normalizer_version TEXT NOT NULL,
    risk_policy_version TEXT NOT NULL,
    artifact_manifest_json TEXT NOT NULL DEFAULT '{}',
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evaluation_runs (
    evaluation_run_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('CREATED','RUNNING','COMPLETED','FAILED')),
    dataset_version TEXT NOT NULL,
    model_bundle_id TEXT
        REFERENCES model_bundles(model_bundle_id) ON DELETE SET NULL,
    commit_hash TEXT,
    started_at_utc TEXT,
    ended_at_utc TEXT,
    total_cases INTEGER NOT NULL DEFAULT 0 CHECK (total_cases >= 0),
    scam_cases INTEGER NOT NULL DEFAULT 0 CHECK (scam_cases >= 0),
    legitimate_cases INTEGER NOT NULL DEFAULT 0 CHECK (legitimate_cases >= 0),
    high_risk_recall REAL CHECK (high_risk_recall BETWEEN 0 AND 1),
    false_positive_rate REAL CHECK (false_positive_rate BETWEEN 0 AND 1),
    average_first_warning_ms REAL CHECK (average_first_warning_ms >= 0),
    summary_json TEXT NOT NULL DEFAULT '{}',
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trusted_organizations (
    organization_id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_name TEXT NOT NULL UNIQUE,
    organization_type TEXT NOT NULL,
    country_code TEXT NOT NULL DEFAULT 'IN',
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1)),
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reference_sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL
        CHECK (source_type IN (
            'OFFICIAL_WEBSITE','OFFICIAL_DOCUMENT','OFFICIAL_APP',
            'OFFICIAL_NOTICE','MANUAL_TEST_SOURCE','OTHER'
        )),
    source_title TEXT NOT NULL,
    source_url TEXT,
    publisher TEXT NOT NULL,
    first_verified_at_utc TEXT NOT NULL,
    last_verified_at_utc TEXT NOT NULL,
    expires_at_utc TEXT,
    content_hash TEXT,
    review_status TEXT NOT NULL
        CHECK (review_status IN ('VERIFIED','PENDING_REVIEW','EXPIRED','REJECTED')),
    notes_redacted TEXT
);

CREATE TABLE IF NOT EXISTS organization_aliases (
    alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL
        REFERENCES trusted_organizations(organization_id) ON DELETE CASCADE,
    alias_normalized TEXT NOT NULL,
    language_code TEXT,
    alias_type TEXT NOT NULL DEFAULT 'NAME'
        CHECK (alias_type IN ('NAME','ABBREVIATION','DEPARTMENT','APP','OTHER')),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1)),
    UNIQUE (organization_id, alias_normalized)
);

CREATE TABLE IF NOT EXISTS official_numbers (
    official_number_id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL
        REFERENCES trusted_organizations(organization_id) ON DELETE CASCADE,
    number_normalized TEXT NOT NULL,
    number_hash TEXT,
    number_type TEXT,
    region TEXT,
    purpose TEXT,
    verified_at_utc TEXT NOT NULL,
    expires_at_utc TEXT,
    source_id INTEGER NOT NULL
        REFERENCES reference_sources(source_id) ON DELETE RESTRICT,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1)),
    UNIQUE (organization_id, number_normalized)
);

CREATE TABLE IF NOT EXISTS official_domains (
    domain_id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL
        REFERENCES trusted_organizations(organization_id) ON DELETE CASCADE,
    domain_normalized TEXT NOT NULL,
    purpose TEXT,
    verified_at_utc TEXT NOT NULL,
    expires_at_utc TEXT,
    source_id INTEGER NOT NULL
        REFERENCES reference_sources(source_id) ON DELETE RESTRICT,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1)),
    UNIQUE (organization_id, domain_normalized)
);

CREATE TABLE IF NOT EXISTS organization_policies (
    policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL
        REFERENCES trusted_organizations(organization_id) ON DELETE CASCADE,
    policy_code TEXT NOT NULL,
    policy_text TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    verified_at_utc TEXT NOT NULL,
    expires_at_utc TEXT,
    source_id INTEGER NOT NULL
        REFERENCES reference_sources(source_id) ON DELETE RESTRICT,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1)),
    UNIQUE (organization_id, policy_code)
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    created_at_utc TEXT NOT NULL,
    started_at_utc TEXT,
    ended_at_utc TEXT,
    input_mode TEXT NOT NULL
        CHECK (input_mode IN ('MICROPHONE','REPLAY','MOCK')),
    privacy_mode TEXT NOT NULL
        CHECK (privacy_mode IN ('MAXIMUM_PRIVACY','EVALUATION')),
    lifecycle_state TEXT NOT NULL
        CHECK (lifecycle_state IN (
            'CREATED','LISTENING','ACTIVE','ENDING',
            'FINALIZED','CLEARED','FAILED'
        )),
    call_direction TEXT
        CHECK (call_direction IN ('INCOMING','OUTGOING','REPLAY','UNKNOWN')),
    language_mode TEXT,
    caller_number_hash TEXT,
    audio_saved INTEGER NOT NULL DEFAULT 0 CHECK (audio_saved = 0),
    transcript_saved INTEGER NOT NULL DEFAULT 0 CHECK (transcript_saved IN (0,1)),
    cloud_reasoning_used INTEGER NOT NULL DEFAULT 0
        CHECK (cloud_reasoning_used IN (0,1)),
    model_bundle_id TEXT
        REFERENCES model_bundles(model_bundle_id) ON DELETE SET NULL,
    config_version TEXT NOT NULL,
    maximum_risk REAL NOT NULL DEFAULT 0 CHECK (maximum_risk BETWEEN 0 AND 100),
    final_risk REAL CHECK (final_risk BETWEEN 0 AND 100),
    final_band TEXT
        CHECK (final_band IS NULL OR final_band IN ('LOW','CAUTION','HIGH','CRITICAL')),
    deletion_due_at_utc TEXT,
    failure_code TEXT
);

CREATE TABLE IF NOT EXISTS utterances (
    utterance_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL
        REFERENCES sessions(session_id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL CHECK (sequence >= 0),
    speaker_role TEXT NOT NULL DEFAULT 'UNKNOWN'
        CHECK (speaker_role IN ('CALLER','USER','UNKNOWN')),
    started_ms INTEGER NOT NULL CHECK (started_ms >= 0),
    ended_ms INTEGER NOT NULL CHECK (ended_ms >= started_ms),
    redacted_text TEXT,
    normalized_text_hash TEXT,
    language_code TEXT,
    asr_confidence REAL CHECK (asr_confidence BETWEEN 0 AND 1),
    asr_model_id TEXT NOT NULL,
    asr_latency_ms INTEGER CHECK (asr_latency_ms >= 0),
    forced_split INTEGER NOT NULL DEFAULT 0 CHECK (forced_split IN (0,1)),
    created_at_utc TEXT NOT NULL,
    UNIQUE (session_id, sequence)
);

CREATE TABLE IF NOT EXISTS evidence_events (
    evidence_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL
        REFERENCES sessions(session_id) ON DELETE CASCADE,
    event_sequence INTEGER NOT NULL CHECK (event_sequence >= 0),
    occurred_ms INTEGER NOT NULL CHECK (occurred_ms >= 0),
    evidence_type TEXT NOT NULL,
    label_code TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    score_delta REAL NOT NULL DEFAULT 0,
    risk_floor REAL CHECK (risk_floor BETWEEN 0 AND 100),
    source_type TEXT NOT NULL
        CHECK (source_type IN ('RULE','ML','LLM','IDENTITY','COMMUNITY','SYSTEM')),
    source_version TEXT NOT NULL,
    evidence_text_redacted TEXT,
    supporting_utterance_ids_json TEXT NOT NULL DEFAULT '[]',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    superseded_by_evidence_id TEXT
        REFERENCES evidence_events(evidence_id) ON DELETE SET NULL,
    created_at_utc TEXT NOT NULL,
    UNIQUE (session_id, event_sequence)
);

CREATE TABLE IF NOT EXISTS risk_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL
        REFERENCES sessions(session_id) ON DELETE CASCADE,
    state_version INTEGER NOT NULL CHECK (state_version >= 0),
    occurred_ms INTEGER NOT NULL CHECK (occurred_ms >= 0),
    risk_index REAL NOT NULL CHECK (risk_index BETWEEN 0 AND 100),
    risk_band TEXT NOT NULL
        CHECK (risk_band IN ('LOW','CAUTION','HIGH','CRITICAL')),
    decision_code TEXT NOT NULL,
    hard_floor REAL NOT NULL DEFAULT 0 CHECK (hard_floor BETWEEN 0 AND 100),
    component_scores_json TEXT NOT NULL DEFAULT '{}',
    reason_codes_json TEXT NOT NULL DEFAULT '[]',
    evidence_ids_json TEXT NOT NULL DEFAULT '[]',
    headline_code TEXT,
    created_at_utc TEXT NOT NULL,
    UNIQUE (session_id, state_version)
);

CREATE TABLE IF NOT EXISTS identity_claims (
    claim_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL
        REFERENCES sessions(session_id) ON DELETE CASCADE,
    utterance_id TEXT
        REFERENCES utterances(utterance_id) ON DELETE SET NULL,
    claimed_name_text_redacted TEXT,
    canonical_organization_id INTEGER
        REFERENCES trusted_organizations(organization_id) ON DELETE SET NULL,
    organization_type TEXT,
    department_text_redacted TEXT,
    role_text_redacted TEXT,
    evidence_text_redacted TEXT NOT NULL,
    confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS verification_results (
    verification_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL
        REFERENCES sessions(session_id) ON DELETE CASCADE,
    claim_id TEXT
        REFERENCES identity_claims(claim_id) ON DELETE CASCADE,
    status_code TEXT NOT NULL
        CHECK (status_code IN (
            'VERIFIED','UNVERIFIED','MISMATCH','POLICY_CONTRADICTION',
            'KNOWN_REPORTED_RISK','ORGANIZATION_NOT_IN_DIRECTORY',
            'INSUFFICIENT_DATA'
        )),
    number_match INTEGER CHECK (number_match IN (0,1)),
    domain_match INTEGER CHECK (domain_match IN (0,1)),
    confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    policy_contradictions_json TEXT NOT NULL DEFAULT '[]',
    source_record_ids_json TEXT NOT NULL DEFAULT '[]',
    safe_wording_code TEXT NOT NULL,
    checked_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS community_patterns (
    pattern_id TEXT PRIMARY KEY,
    schema_version INTEGER NOT NULL CHECK (schema_version >= 1),
    campaign_code TEXT,
    organization_type TEXT,
    scenario_code TEXT,
    tactic_codes_json TEXT NOT NULL DEFAULT '[]',
    requested_action_codes_json TEXT NOT NULL DEFAULT '[]',
    threat_codes_json TEXT NOT NULL DEFAULT '[]',
    payment_rail TEXT,
    channel_switch TEXT,
    language_family TEXT,
    country_code TEXT NOT NULL DEFAULT 'IN',
    month_bucket TEXT,
    verification_tier TEXT NOT NULL DEFAULT 'SYNTHETIC'
        CHECK (verification_tier IN (
            'SYNTHETIC','UNVERIFIED_COMMUNITY','REVIEWED','TRUSTED'
        )),
    independent_report_count INTEGER NOT NULL DEFAULT 0
        CHECK (independent_report_count >= 0),
    confidence REAL NOT NULL DEFAULT 0 CHECK (confidence BETWEEN 0 AND 1),
    first_seen_at_utc TEXT,
    last_seen_at_utc TEXT,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1))
);

CREATE TABLE IF NOT EXISTS pattern_matches (
    match_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL
        REFERENCES sessions(session_id) ON DELETE CASCADE,
    pattern_id TEXT NOT NULL
        REFERENCES community_patterns(pattern_id) ON DELETE RESTRICT,
    similarity REAL NOT NULL CHECK (similarity BETWEEN 0 AND 1),
    component_scores_json TEXT NOT NULL DEFAULT '{}',
    match_reasons_json TEXT NOT NULL DEFAULT '[]',
    data_source_code TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    UNIQUE (session_id, pattern_id)
);

CREATE TABLE IF NOT EXISTS user_feedback (
    feedback_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL
        REFERENCES sessions(session_id) ON DELETE CASCADE,
    risk_snapshot_id TEXT
        REFERENCES risk_snapshots(snapshot_id) ON DELETE SET NULL,
    feedback_type TEXT NOT NULL
        CHECK (feedback_type IN (
            'CORRECT_WARNING','FALSE_POSITIVE','FALSE_NEGATIVE',
            'INCORRECT_REASON','OTHER'
        )),
    label_code TEXT,
    comment_redacted TEXT,
    source TEXT NOT NULL DEFAULT 'EVALUATION'
        CHECK (source IN ('EVALUATION','USER_UI','TEAM_REVIEW')),
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS system_metrics (
    metric_id TEXT PRIMARY KEY,
    session_id TEXT
        REFERENCES sessions(session_id) ON DELETE CASCADE,
    evaluation_run_id TEXT
        REFERENCES evaluation_runs(evaluation_run_id) ON DELETE CASCADE,
    component TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT NOT NULL,
    occurred_ms INTEGER CHECK (occurred_ms >= 0),
    tags_json TEXT NOT NULL DEFAULT '{}',
    created_at_utc TEXT NOT NULL,
    CHECK (session_id IS NOT NULL OR evaluation_run_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_utterances_session_time ON utterances(session_id, started_ms);
CREATE INDEX IF NOT EXISTS idx_evidence_session_time ON evidence_events(session_id, occurred_ms);
CREATE INDEX IF NOT EXISTS idx_evidence_label ON evidence_events(label_code, created_at_utc);
CREATE INDEX IF NOT EXISTS idx_risk_session_version ON risk_snapshots(session_id, state_version);
CREATE INDEX IF NOT EXISTS idx_identity_claim_session ON identity_claims(session_id, created_at_utc);
CREATE INDEX IF NOT EXISTS idx_alias_normalized ON organization_aliases(alias_normalized, active);
CREATE INDEX IF NOT EXISTS idx_official_number ON official_numbers(number_normalized, active);
CREATE INDEX IF NOT EXISTS idx_official_domain ON official_domains(domain_normalized, active);
CREATE INDEX IF NOT EXISTS idx_policy_org_code ON organization_policies(organization_id, policy_code, active);
CREATE INDEX IF NOT EXISTS idx_pattern_scenario ON community_patterns(scenario_code, active);
CREATE INDEX IF NOT EXISTS idx_metric_session ON system_metrics(session_id, component, metric_name);