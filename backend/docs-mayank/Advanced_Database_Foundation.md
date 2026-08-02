# Mayank - Advanced Database Foundation, Privacy Persistence, Community Intelligence, Integration Contracts, and QA Handbook

> **Project:** SurakshaCall AI  
> **Role owner:** Mayank  
> **Primary responsibility:** Build the complete local database foundation so every backend, AI, identity, community, evaluation, and frontend module can integrate without writing SQL or weakening privacy.  
> **Prototype database:** SQLite  
> **Temporary live state:** RAM  
> **Controlled artifacts:** Filesystem  
> **Community matching:** Structured privacy-safe fingerprints + Weighted Jaccard similarity  
> **Vector database:** Not required for the current SIH prototype  
> **Critical project reality:** The backend and frontend are not fully implemented yet. Therefore, this handbook uses a **contract-first, standalone-first, mock-integrated-first** plan so Mayank can complete the database foundation without waiting for Ron's backend or Palak's frontend.

---

## Document Status

| Field | Final decision |
|---|---|
| Database architecture | One local SQLite database |
| Raw audio storage | Prohibited |
| Unredacted transcript storage | Prohibited by default |
| Default privacy mode | `MAXIMUM_PRIVACY` |
| Test mode | `EVALUATION` |
| Database access | Repository layer only |
| Concurrency strategy | WAL + short transactions; single writer only if needed |
| Frontend access | Through backend events/API only; never direct SQLite |
| Backend dependency during Mayank's work | None for the core foundation |
| Frontend dependency during Mayank's work | None; use contract fixtures and mock events |
| ChromaDB / PostgreSQL / Redis | Not now |
| Completion rule | Implemented + tested + mock-integrated + later real-integrated on the final laptop |

---

# 0. Comparison of the Existing Files and Final Resolution

This handbook reconciles the following project materials:

1. `06_Mayank_Database_Community_Intelligence_Privacy_and_QA (1).md`
2. `database-files-about.md`
3. `Database-rest-data.txt`
4. `SurakshaCall Database Foundation Specification.pdf`
5. `SurakshaCall_AI_Advanced_Technical_Working_Handbook`
6. the full SurakshaCall project blueprint

## 0.1 What the original Mayank role correctly assigned

The original role already made Mayank responsible for:

- SQLite schema and initialization;
- repository functions;
- session, utterance, evidence, and risk persistence;
- trusted-directory persistence;
- community fingerprints and similarity;
- privacy retention and cleanup;
- QA status and regression coordination;
- evaluation runs and metrics;
- frontend data integration;
- database failure handling.

These responsibilities remain valid.

## 0.2 What `database-files-about.md` proves

The implementation explanation shows that the current foundation has at least been started through:

- `schema.sql`;
- `connection.py`;
- `seed.py`;
- `repositories.py`;
- `privacy/redaction.py`;
- `privacy/retention.py`;
- `privacy/status.py`;
- community fingerprint, weights, matcher, and service;
- cleanup behavior.

However, a file being described does **not** prove that every required method, constraint, integration path, and test is complete. This handbook therefore treats the existing code as a foundation to audit, not as automatically finished work.

## 0.3 What `Database-rest-data.txt` added

The remaining-work analysis correctly identified high-value additions:

- `identity_claims`;
- `organization_aliases`;
- `official_domains`;
- `organization_policies`;
- `reference_sources`;
- `model_bundles`;
- `user_feedback`;
- indexes;
- transactions;
- WAL;
- backup;
- fuller testing and integration.

It also correctly rejected unnecessary infrastructure such as ChromaDB for the current structured and small pattern corpus.

## 0.4 What the attached Database Foundation Specification adds

The attached specification turns the earlier notes into a more complete database architecture with:

- 18 recommended application tables;
- normalized trusted-identity records;
- source provenance;
- model/version registry;
- user feedback;
- evaluation and metrics;
- transaction, WAL, busy-timeout, backup, failure, and QA requirements;
- repository groups;
- a final implementation order.

This handbook adopts that database foundation, but changes the execution strategy because the backend and frontend are incomplete.

## 0.5 Final naming and architecture decisions

| Earlier variation | Final choice | Reason |
|---|---|---|
| `community_matches` | `pattern_matches` | Matches the final specification and clearly identifies what is matched |
| `caller_number_redacted` | `caller_number_hash` | Better privacy; no raw caller number in durable storage |
| Organization aliases/numbers/domains in JSON | Separate normalized tables | Easier lookup, indexing, provenance, and updates |
| One giant repository file with unrelated functions | Repository classes grouped by domain | Cleaner contracts and future SQLite-to-PostgreSQL migration |
| Frontend reads database | Forbidden | Frontend consumes typed backend events only |
| Agents write SQL directly | Forbidden | Agents call repositories or send persistence commands |
| ChromaDB | Not used | Structured fingerprint + Weighted Jaccard is enough |
| Integration considered one state | Split into mock and real integration | Backend/frontend are unfinished, so Mayank must not be blocked |
| "Designed" considered "implemented" | Forbidden | Completion requires code, tests, and reproducible execution |

## 0.6 New completion states for this project

Every database feature must use one of these statuses:

```text
NOT_STARTED
SKELETON_CREATED
IMPLEMENTED
UNIT_TESTED
MOCK_INTEGRATED
REAL_INTEGRATED
DEMO_VERIFIED
```

A table existing in `schema.sql` is only `IMPLEMENTED` after:

- its constraints are valid;
- its repository functions exist;
- its tests pass;
- seed/reset handles it where applicable;
- privacy rules cover it;
- failure behavior is defined.

A feature is not `REAL_INTEGRATED` until the actual backend or frontend uses it.

---

# 1. Mayank's Mission

Mayank is not only "the database member."

His complete role is:

> **Database architecture + privacy-safe persistence + trusted intelligence storage + community intelligence + reproducibility + evaluation + QA + integration contracts.**

The system must always be able to answer:

- Which session was active?
- Which evidence was detected?
- Which module produced the evidence?
- Which exact model, rule, prompt, and risk policy versions were used?
- How did risk change over time?
- What identity did the caller claim?
- What trusted information was checked?
- Was the result verified, unverified, contradictory, or insufficient?
- Which anonymous campaign pattern was similar?
- Why was it similar?
- What data was persisted?
- What private data was not persisted?
- Was cleanup completed?
- Did the database fail?
- Did protection continue in memory?
- Which tests and evaluation run produced the reported metrics?

---

# 2. Critical Adaptation: Backend and Frontend Are Not Ready

Mayank must **not wait** for the rest of the application.

He must build the database as a standalone Python subsystem with stable interfaces.

## 2.1 Standalone-first rule

The core database package must not import:

- FastAPI;
- WebSocket classes;
- React/Next.js types;
- microphone libraries;
- Whisper;
- the local LLM runtime;
- UI components.

It may use:

- Python standard library;
- `sqlite3`;
- Pydantic or dataclasses for typed contracts;
- `pytest`;
- safe utility packages already agreed by the team.

## 2.2 What Mayank builds before the backend exists

Mayank can fully build and test:

- database schema;
- connection manager;
- transactions;
- repositories;
- seed/reset;
- trusted directory;
- community matcher;
- redaction and retention;
- cleanup;
- model bundle registry;
- feedback persistence;
- metrics;
- evaluation export;
- backup/restore;
- mock pipeline;
- JSON event fixtures;
- contract documentation;
- failure tests.

## 2.3 What Mayank prepares for the backend

Mayank provides Ron with:

- repository method signatures;
- domain models;
- transaction service;
- mock events;
- error classes;
- example usage;
- setup commands;
- database health check;
- integration tests.

Ron should be able to integrate the database without modifying SQL.

## 2.4 What Mayank prepares for the frontend

Mayank provides Palak with:

- stable event examples;
- JSON schema or TypeScript-ready field definitions;
- explicit null behavior;
- privacy status events;
- database degradation events;
- risk and evidence history examples;
- reset/session-cleared examples.

Mayank does **not** need to build Palak's UI. He must prove that the data contract is safe and stable.

## 2.5 Mock integration is mandatory

Until the real backend exists, create a mock vertical slice:

```text
Mock TranscriptFinal
        ↓
Mock DetectionResult
        ↓
Repository persistence
        ↓
Mock Identity lookup
        ↓
Community match
        ↓
Mock RiskDecision
        ↓
Risk snapshot
        ↓
Outbound JSON event fixture
        ↓
Cleanup
```

This proves the database foundation independently.

---

# 3. Fixed Engineering Boundaries

## 3.1 Database responsibilities

The database has five responsibilities:

1. **Session audit spine**  
   Redacted session, evidence, and risk history.

2. **Trusted reference store**  
   Organizations, aliases, numbers, domains, policies, and source provenance.

3. **Community intelligence store**  
   Anonymous structured campaign patterns and explainable matches.

4. **Model and evaluation registry**  
   Versions, metrics, feedback, and evaluation runs.

5. **Privacy enforcement and recovery**  
   Retention checks, cleanup, backup safety, and database failure behavior.

## 3.2 Database non-responsibilities

The database does not:

- capture audio;
- store raw audio;
- transcribe speech;
- classify manipulation;
- calculate the Risk Index;
- declare that a caller is a criminal;
- decide that a similarity match proves fraud;
- fetch arbitrary websites during a live call;
- send UI warnings directly;
- expose private text to the frontend;
- train models automatically from feedback.

## 3.3 Storage policy

| Data | Location | Default retention |
|---|---|---|
| PCM audio | RAM ring buffer | Seconds only |
| Unredacted transcript | RAM | Active session only |
| Redacted utterance | SQLite, optional | Policy-controlled |
| Evidence event | SQLite | Policy-controlled |
| Risk snapshot | SQLite | Policy-controlled |
| Trusted directory | SQLite | Persistent, freshness-reviewed |
| Community fingerprint | SQLite | Persistent, synthetic/opt-in |
| Model metadata | SQLite/filesystem | Persistent |
| Synthetic audio | Filesystem | Controlled test artifact |
| Evaluation CSV | Filesystem | Controlled output |
| Backup | Filesystem | Must contain only permitted data |

## 3.4 Privacy wording

Use:

> Raw audio is held only in a short in-memory buffer and is not stored in SQLite. In maximum-privacy mode, unredacted transcript is also memory-only. Durable records contain only permitted redacted text, structured evidence, risk history, trusted reference data, anonymous community fingerprints, versions, and evaluation metrics.

---

# 4. Final Runtime Data Architecture

```text
Phone speaker / replay WAV
          |
          v
Audio + VAD + Whisper
          |
          v
TranscriptFinal
          |
          +-------------------------------+
          |                               |
          v                               v
Live RAM conversation state        Privacy redactor
          |                               |
          v                               v
Rules / ML / LLM / identity         Allowed persistence data
          |                               |
          +---------------+---------------+
                          |
                          v
                   Repository layer
                          |
                          v
                    SQLite WAL file
                          |
      +-------------------+-------------------+
      |                   |                   |
      v                   v                   v
Session/evidence      Trusted identity    Community patterns
and risk history      and provenance      and matches
      |                   |                   |
      +-------------------+-------------------+
                          |
                          v
                 Metrics and evaluation
```

## 4.1 Frontend path

```text
SQLite
   ↓
Repository
   ↓
Backend service
   ↓
HTTP/WebSocket event
   ↓
Frontend
```

Never:

```text
Frontend → SQLite
```

## 4.2 Failure path

```text
AI calculates a warning
        ↓
Persistence attempt fails
        ↓
Bounded retry
        ↓
RAM-only degraded mode
        ↓
Warning still reaches UI
        ↓
Database health event reports the failure
```

The database must never become the reason a safety warning disappears.

---

# 5. Final Repository and Folder Structure

```text
suraksha-call-ai/
├── backend/
│   ├── app/
│   │   ├── contracts/
│   │   │   ├── __init__.py
│   │   │   ├── database_models.py
│   │   │   ├── pipeline_events.py
│   │   │   └── ui_events.py
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── connection.py
│   │   │   ├── schema.sql
│   │   │   ├── seed.py
│   │   │   ├── repositories.py
│   │   │   ├── services.py
│   │   │   ├── writer.py
│   │   │   ├── cleanup.py
│   │   │   ├── backup.py
│   │   │   ├── health.py
│   │   │   ├── errors.py
│   │   │   └── migrations/
│   │   │       └── 001_initial.sql
│   │   │
│   │   ├── privacy/
│   │   │   ├── __init__.py
│   │   │   ├── redaction.py
│   │   │   ├── retention.py
│   │   │   ├── validators.py
│   │   │   └── status.py
│   │   │
│   │   └── community/
│   │       ├── __init__.py
│   │       ├── fingerprint.py
│   │       ├── weights.py
│   │       ├── matcher.py
│   │       └── service.py
│   │
│   └── tests/
│       ├── database/
│       │   ├── test_schema.py
│       │   ├── test_connection.py
│       │   ├── test_transactions.py
│       │   ├── test_sessions.py
│       │   ├── test_utterances.py
│       │   ├── test_evidence.py
│       │   ├── test_risk.py
│       │   ├── test_identity.py
│       │   ├── test_community.py
│       │   ├── test_models_feedback.py
│       │   ├── test_metrics_evaluation.py
│       │   ├── test_cleanup.py
│       │   ├── test_backup_restore.py
│       │   └── test_failure_mode.py
│       ├── privacy/
│       │   ├── test_redaction.py
│       │   ├── test_retention.py
│       │   └── test_no_leakage.py
│       ├── contracts/
│       │   └── test_event_contracts.py
│       └── integration/
│           ├── test_mock_vertical_slice.py
│           └── test_replay_fixture_persistence.py
│
├── data/
│   ├── database/
│   │   └── suraksha.db
│   ├── backups/
│   ├── seed/
│   │   ├── trusted_organizations.json
│   │   ├── reference_sources.json
│   │   ├── organization_aliases.json
│   │   ├── organization_policies.json
│   │   └── community_patterns.json
│   └── evaluation/
│       ├── fixtures/
│       └── exports/
│
├── scripts/
│   ├── init_database.py
│   ├── reset_database.py
│   ├── database_smoke_test.py
│   ├── run_mock_database_pipeline.py
│   ├── export_evaluation.py
│   ├── backup_database.py
│   └── inspect_database.py
│
└── docs/
    ├── database-readme.md
    ├── data-dictionary.md
    ├── privacy.md
    ├── retention.md
    ├── integration-contracts.md
    ├── database-status.md
    ├── test-status.md
    └── evaluation.md
```

## 5.1 Temporary compatibility rule

If the current project already contains:

```text
backend/app/database/repositories.py
```

do not immediately split it into many files if that would break working code. It may contain repository classes in one file first. Split only after tests are stable.

## 5.2 No circular dependency

The dependency direction should be:

```text
contracts
    ↓
privacy
    ↓
database repositories
    ↓
database services
    ↓
backend adapters later
```

The database package must never import the FastAPI application.

---

# 6. Phase 0 - Audit the Current Implementation

Before writing new features, compare the actual code to the specification.

## 6.1 Audit commands

```bash
python -m app.database.seed
python -m app.database.seed
python -m app.database.seed --reset
pytest backend/tests/database -q
```

## 6.2 Audit checklist

For every existing table, record:

```text
Table:
Exists:
Primary key:
Foreign keys:
Unique constraints:
CHECK constraints:
Indexes:
Repository methods:
Seed data:
Unit tests:
Privacy rule:
Cleanup rule:
Integration status:
Known defect:
```

## 6.3 Required current-code audit

- [ ] `schema.sql` runs on an empty directory.
- [ ] `schema.sql` runs after reset.
- [ ] Seed is idempotent.
- [ ] Foreign keys are actually enabled on every connection.
- [ ] No SQL string interpolation is used for user data.
- [ ] No raw transcript is logged.
- [ ] No raw audio table exists.
- [ ] Maximum-privacy retention prevents utterance persistence.
- [ ] Cleanup deletes prohibited data.
- [ ] Weighted Jaccard uses one configuration source.
- [ ] Community patterns contain no private text.
- [ ] Repository exceptions are handled.
- [ ] Tests run on a temporary database, not the real demo database.

## 6.4 Output

Create:

```text
docs/database-status.md
```

Use:

| Component | Current status | Evidence | Remaining action | Owner |
|---|---|---|---|---|

Do not mark a component complete because documentation describes it.

---

# 7. Phase 1 - Freeze Typed Contracts Before Backend Integration

Because the backend is incomplete, define the data shapes now.

## 7.1 Contract principles

- IDs are strings.
- UTC timestamps are ISO-8601 strings.
- Durations inside a session are integer milliseconds.
- Enums use uppercase canonical codes.
- Unknown values are explicit `null`, not missing whenever possible.
- Redacted fields are named with `_redacted`.
- The browser never receives raw private values.
- Every event has `schema_version`.
- Database write payloads and UI events are separate contracts.

## 7.2 Minimum pipeline contracts

```python
from typing import Literal
from pydantic import BaseModel, Field

PrivacyMode = Literal["MAXIMUM_PRIVACY", "EVALUATION"]
InputMode = Literal["MICROPHONE", "REPLAY", "MOCK"]

class TranscriptFinal(BaseModel):
    event_id: str
    session_id: str
    utterance_id: str
    sequence: int
    speaker: Literal["CALLER", "USER", "UNKNOWN"]
    started_ms: int = Field(ge=0)
    ended_ms: int = Field(ge=0)
    raw_text: str
    language_code: str | None = None
    asr_confidence: float | None = Field(default=None, ge=0, le=1)
    asr_model_id: str
    occurred_at_utc: str

class DetectionResult(BaseModel):
    evidence_id: str
    session_id: str
    occurred_ms: int = Field(ge=0)
    evidence_type: str
    label_code: str
    severity: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0, le=1)
    score_delta: float
    risk_floor: float | None = Field(default=None, ge=0, le=100)
    source_type: Literal["RULE", "ML", "LLM", "IDENTITY", "COMMUNITY", "SYSTEM"]
    source_version: str
    supporting_utterance_ids: list[str]
    evidence_text_redacted: str | None = None
    metadata: dict

class RiskDecision(BaseModel):
    snapshot_id: str
    session_id: str
    state_version: int
    occurred_ms: int
    risk_index: float = Field(ge=0, le=100)
    risk_band: Literal["LOW", "CAUTION", "HIGH", "CRITICAL"]
    decision_code: str
    hard_floor: float = Field(ge=0, le=100)
    reason_codes: list[str]
    evidence_ids: list[str]
    component_scores: dict[str, float]
    headline_code: str | None = None

class DatabaseHealthEvent(BaseModel):
    event: Literal["database_health"]
    session_id: str | None
    status: Literal["AVAILABLE", "DEGRADED", "UNAVAILABLE", "RECOVERED"]
    persistence_enabled: bool
    safe_fallback_active: bool
    error_code: str | None
    occurred_at_utc: str
```

## 7.3 Contract fixtures

Create JSON fixtures:

```text
data/evaluation/fixtures/
├── transcript_final.json
├── detection_result.json
├── identity_claim.json
├── community_match.json
├── risk_decision.json
├── privacy_status.json
├── database_degraded.json
└── session_cleared.json
```

These allow Ron and Palak to work before full integration.

## 7.4 Contract version rule

When a field is added:

- preserve old meaning;
- increment schema version only for breaking changes;
- document the change;
- update fixture tests;
- notify Ron and Palak.

---

# 8. Phase 2 - Final SQLite Schema

## 8.1 Final table set

### Core session data

1. `sessions`
2. `utterances`
3. `evidence_events`
4. `risk_snapshots`

### Trusted identity data

5. `trusted_organizations`
6. `reference_sources`
7. `organization_aliases`
8. `official_numbers`
9. `official_domains`
10. `organization_policies`
11. `identity_claims`
12. `verification_results`

### Community intelligence

13. `community_patterns`
14. `pattern_matches`

### Reproducibility and evaluation

15. `model_bundles`
16. `user_feedback`
17. `evaluation_runs`
18. `system_metrics`

An optional `schema_migrations` table may be added for the simple migration runner. It is infrastructure, not an application-data table.

## 8.2 Complete recommended `schema.sql`

```sql
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

CREATE INDEX IF NOT EXISTS idx_utterances_session_time
    ON utterances(session_id, started_ms);

CREATE INDEX IF NOT EXISTS idx_evidence_session_time
    ON evidence_events(session_id, occurred_ms);

CREATE INDEX IF NOT EXISTS idx_evidence_label
    ON evidence_events(label_code, created_at_utc);

CREATE INDEX IF NOT EXISTS idx_risk_session_version
    ON risk_snapshots(session_id, state_version);

CREATE INDEX IF NOT EXISTS idx_identity_claim_session
    ON identity_claims(session_id, created_at_utc);

CREATE INDEX IF NOT EXISTS idx_alias_normalized
    ON organization_aliases(alias_normalized, active);

CREATE INDEX IF NOT EXISTS idx_official_number
    ON official_numbers(number_normalized, active);

CREATE INDEX IF NOT EXISTS idx_official_domain
    ON official_domains(domain_normalized, active);

CREATE INDEX IF NOT EXISTS idx_policy_org_code
    ON organization_policies(organization_id, policy_code, active);

CREATE INDEX IF NOT EXISTS idx_pattern_scenario
    ON community_patterns(scenario_code, active);

CREATE INDEX IF NOT EXISTS idx_metric_session
    ON system_metrics(session_id, component, metric_name);
```

## 8.3 Schema rules

- `audio_saved` is constrained to `0`.
- `utterances.redacted_text` may be `NULL` in maximum privacy.
- A raw phone number is never stored in `sessions`.
- Unknown verification must not become fraud.
- Community patterns contain categories, not conversation text.
- Every risk score is constrained to `0..100`.
- Every confidence is constrained to `0..1`.
- Foreign keys are mandatory.
- All timestamps use UTC strings.
- All JSON columns must be serialized by shared helpers.

## 8.4 JSON validation

SQLite may not enforce JSON validity on all environments. Repositories must validate JSON before insertion.

Create helpers:

```python
def dumps_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

def loads_json(value: str) -> object:
    return json.loads(value)
```

Unit-test every JSON field.

---

# 9. Phase 3 - Connection, WAL, Transactions, and Health

## 9.1 `config.py`

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    path: Path
    busy_timeout_ms: int = 5000
    synchronous: str = "NORMAL"
    enable_wal: bool = True
```

The default path should be resolved from the project root, not the current working directory.

## 9.2 `connection.py` responsibilities

- create the parent directory;
- connect with a timeout;
- use `sqlite3.Row`;
- enable foreign keys on every connection;
- enable WAL for the file database;
- set busy timeout;
- close cleanly;
- provide read and transaction context managers;
- translate low-level errors into database-specific exceptions.

## 9.3 Recommended implementation pattern

```python
from contextlib import contextmanager
import sqlite3

@contextmanager
def open_connection(config: DatabaseConfig):
    config.path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        config.path,
        timeout=config.busy_timeout_ms / 1000,
        isolation_level=None,
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row

    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(f"PRAGMA busy_timeout = {config.busy_timeout_ms};")
        conn.execute(f"PRAGMA synchronous = {config.synchronous};")
        conn.execute("PRAGMA temp_store = MEMORY;")

        if config.enable_wal and str(config.path) != ":memory:":
            conn.execute("PRAGMA journal_mode = WAL;")

        yield conn
    finally:
        conn.close()

@contextmanager
def transaction(conn: sqlite3.Connection):
    try:
        conn.execute("BEGIN IMMEDIATE;")
        yield conn
        conn.execute("COMMIT;")
    except Exception:
        conn.execute("ROLLBACK;")
        raise
```

## 9.4 Transaction service

Related operations must use one transaction:

```text
Insert evidence
Insert risk snapshot
Update session maximum risk
Insert metric
```

Create a service method such as:

```python
persist_decision_bundle(
    evidence_events: list[DetectionResult],
    risk_decision: RiskDecision,
    metrics: list[MetricRecord],
) -> None
```

The orchestration module should call one service instead of manually coordinating four repository calls.

## 9.5 Error hierarchy

```python
class DatabaseError(Exception): ...
class DatabaseUnavailableError(DatabaseError): ...
class DatabaseLockedError(DatabaseError): ...
class DatabaseConstraintError(DatabaseError): ...
class DatabaseCorruptionError(DatabaseError): ...
class PrivacyViolationError(DatabaseError): ...
class SerializationError(DatabaseError): ...
```

Do not expose raw SQL or private data in user-facing errors.

## 9.6 Database health check

A health check should verify:

- connection opens;
- foreign keys are on;
- WAL is active;
- schema version exists;
- a read query works;
- database file is writable where expected.

Output:

```json
{
  "status": "AVAILABLE",
  "foreign_keys": true,
  "journal_mode": "wal",
  "schema_version": 1,
  "writable": true
}
```

---

# 10. Phase 4 - Repository Layer

## 10.1 Repository rule

No AI agent, API route, WebSocket handler, frontend code, or evaluation script may execute raw SQL directly.

## 10.2 Repository groups

```python
class SessionRepository: ...
class UtteranceRepository: ...
class EvidenceRepository: ...
class RiskRepository: ...
class IdentityRepository: ...
class CommunityRepository: ...
class ModelRepository: ...
class FeedbackRepository: ...
class EvaluationRepository: ...
```

## 10.3 Session repository

Required methods:

```python
create_session(...)
get_session(session_id)
update_session_state(session_id, lifecycle_state)
mark_session_failed(session_id, failure_code)
update_maximum_risk(session_id, risk_index)
end_session(session_id, final_risk, final_band)
mark_session_cleared(session_id)
delete_session(session_id)
```

Rules:

- Session IDs are generated outside or by a shared ID helper.
- `audio_saved` cannot be changed to true.
- Lifecycle transitions must be validated.
- `maximum_risk` cannot decrease.
- Ending an unknown session raises a typed error.

## 10.4 Utterance repository

```python
add_redacted_utterance(...)
get_session_utterances(session_id)
delete_session_utterances(session_id)
count_session_utterances(session_id)
```

Rules:

- Check retention policy before insert.
- Refuse raw text.
- The input field must be named `redacted_text`.
- In maximum privacy, return a skipped-persistence result rather than silently storing.
- Sequence must be unique per session.

## 10.5 Evidence repository

```python
add_evidence_event(...)
add_evidence_events(...)
get_session_evidence(session_id)
get_evidence_by_label(session_id, label_code)
supersede_evidence(old_id, new_id)
```

Rules:

- Evidence text must be redacted.
- Supporting utterance IDs must be serialized safely.
- Source type and source version are mandatory.
- Evidence is immutable except for `superseded_by_evidence_id`.

## 10.6 Risk repository

```python
add_risk_snapshot(...)
get_latest_risk(session_id)
get_risk_history(session_id)
get_maximum_risk(session_id)
```

Rules:

- The database stores risk; it never calculates it.
- `state_version` must be unique.
- The snapshot must reference valid evidence IDs at the service-validation layer.
- Critical risk history must not disappear during the session.

## 10.7 Identity repository

```python
save_identity_claim(...)
find_organization_by_alias(alias)
get_organization(organization_id)
find_official_number(number_normalized, organization_id=None)
find_official_domain(domain_normalized, organization_id=None)
get_organization_policies(organization_id)
get_reference_sources(source_ids)
save_verification_result(...)
get_latest_verification(session_id)
```

Rules:

- Alias matching is normalized and case-insensitive.
- Expired data is returned with freshness state, not treated as verified.
- Unknown number means `UNVERIFIED`, not scam.
- Policy contradiction is a separate result.
- Repository returns source IDs for explainability.

## 10.8 Community repository

```python
get_active_patterns(...)
find_candidate_patterns(...)
save_pattern_match(...)
get_session_matches(session_id)
upsert_synthetic_pattern(...)
deactivate_pattern(pattern_id)
```

For the prototype, `find_candidate_patterns` can filter by:

- active;
- country;
- organization type;
- scenario code;
- language family.

If filtering produces no rows, match all active small patterns.

## 10.9 Model repository

```python
register_model_bundle(...)
get_model_bundle(model_bundle_id)
get_latest_model_bundle()
```

Rules:

- Model bundles are immutable.
- When a model or prompt changes, insert a new bundle.
- `NOT_SELECTED` may be used only for a development bundle.
- The final demo bundle must contain actual versions and artifact hashes where available.

## 10.10 Feedback repository

```python
save_user_feedback(...)
get_session_feedback(session_id)
get_feedback_summary(evaluation_run_id=None)
```

The UI is incomplete, so add a CLI and mock fixture to exercise feedback now.

## 10.11 Evaluation repository

```python
create_evaluation_run(...)
start_evaluation_run(...)
complete_evaluation_run(...)
fail_evaluation_run(...)
save_metric(...)
save_metrics(...)
get_evaluation_results(evaluation_run_id)
export_evaluation_csv(evaluation_run_id, output_path)
```

## 10.12 Return types

Repositories should return typed domain objects or dictionaries with documented fields. Do not return raw SQLite rows beyond the repository boundary.

---

# 11. Phase 5 - Seed and Reset

## 11.1 Seed goals

Seed must create enough data for:

- identity alias lookup;
- official-number lookup;
- official-domain lookup;
- policy contradiction;
- reference provenance;
- community matching;
- mock evaluation;
- model bundle resolution.

## 11.2 Minimum safe seed data

- 3-5 trusted organizations;
- 3-8 aliases per organization;
- official demo/test numbers;
- official domains;
- safety policies such as `NO_OTP_REQUEST`, `NO_PIN_REQUEST`, `NO_REMOTE_ACCESS`;
- reference-source records;
- 10-20 synthetic community patterns;
- one development model bundle;
- no private victim information;
- no real call transcript;
- no OTP or account values.

## 11.3 Seed behavior

```bash
python -m app.database.seed
python -m app.database.seed
```

Both commands must produce the same row counts.

Reset:

```bash
python -m app.database.seed --reset
```

Reset must:

1. refuse to run against an unexpected path;
2. close active connections;
3. remove SQLite database, `-wal`, and `-shm` files;
4. recreate schema;
5. insert seed data;
6. run a smoke validation;
7. print row counts.

## 11.4 Idempotent SQL

Use:

- stable IDs;
- `INSERT ... ON CONFLICT DO UPDATE` for maintained reference data;
- `INSERT OR IGNORE` only where ignoring is safe;
- transactions around seed groups.

## 11.5 Seed manifest

Create:

```json
{
  "seed_version": "1.0.0",
  "trusted_source_count": 5,
  "organization_count": 4,
  "community_pattern_count": 15,
  "contains_private_data": false
}
```

---

# 12. Phase 6 - Privacy Engine

## 12.1 Privacy pipeline

```text
Raw transcript in RAM
       ↓
Concept/entity extraction
       ↓
Sensitive-value redaction
       ↓
Retention-policy decision
       ↓
Repository persistence or skip
```

Redaction must happen before persistence, but after extracting the fact that a sensitive request occurred.

## 12.2 Retention modes

### `MAXIMUM_PRIVACY`

```text
Raw audio: RAM only
Raw transcript: RAM only
Redacted transcript: disabled unless explicitly enabled
Evidence: allowed
Risk: allowed
Identity results: allowed
Pattern match: allowed
Metrics: allowed
```

### `EVALUATION`

```text
Synthetic or consented test audio: filesystem input only
Raw audio copied into database: never
Redacted transcript: allowed
Evidence and risk: allowed
Metrics and expected labels: allowed
Feedback: allowed
```

## 12.3 Retention API

```python
class RetentionPolicy:
    def should_persist_utterance(self, privacy_mode: str) -> bool: ...
    def should_persist_evidence(self, privacy_mode: str) -> bool: ...
    def should_persist_risk(self, privacy_mode: str) -> bool: ...
    def should_persist_pattern_match(self, privacy_mode: str) -> bool: ...
    def deletion_due_at(self, privacy_mode: str, started_at_utc: str) -> str | None: ...
```

The repository must call this policy. Do not depend on callers remembering it.

## 12.4 Redaction order

Apply specific patterns before general numeric patterns:

1. URLs and emails;
2. UPI IDs;
3. PAN;
4. Aadhaar;
5. card-like numbers;
6. account numbers;
7. OTP/PIN/CVV values;
8. phone numbers;
9. addresses/names when reliable.

## 12.5 Redaction examples

```text
Raw:
My OTP is 482193 and account number is 123456789012.

Persisted:
My [OTP_REDACTED] and account number is [ACCOUNT_REDACTED].
```

```text
Raw:
Visit fake-bank.example and send money to user@upi.

Persisted:
Visit [URL_REDACTED] and send money to [UPI_REDACTED].
```

## 12.6 Persistence guard

Create a final privacy validator:

```python
validate_safe_for_persistence(record)
```

It should reject:

- suspicious digit sequences;
- raw phone numbers in sessions;
- fields named `raw_text`, `raw_audio`, or `audio_bytes`;
- unredacted email/UPI/URL values where not allowed;
- unrestricted transcript inside metadata JSON;
- secrets inside community fingerprints.

## 12.7 Safe logging

Never log:

```python
logger.info("Transcript: %s", raw_text)
```

Instead log:

```python
logger.info(
    "utterance_persistence",
    extra={
        "session_id": session_id,
        "utterance_id": utterance_id,
        "persisted": persisted,
        "privacy_mode": privacy_mode,
    },
)
```

## 12.8 Privacy status event

```json
{
  "event": "privacy_status",
  "session_id": "S001",
  "raw_audio_saved": false,
  "unredacted_transcript_saved": false,
  "redacted_transcript_saved": false,
  "evidence_saved": true,
  "database_status": "AVAILABLE",
  "cleanup_status": "PENDING"
}
```

---

# 13. Phase 7 - Trusted Identity Foundation

## 13.1 Identity flow

```text
Caller says organization name
          ↓
Identity claim extractor
          ↓
Alias normalization
          ↓
Canonical organization
          ↓
Number/domain lookup
          ↓
Policy lookup
          ↓
Reference provenance
          ↓
Verification result
```

## 13.2 Alias normalization

Normalize:

- Unicode;
- whitespace;
- punctuation;
- case;
- common abbreviations;
- Hindi/English aliases.

Examples:

```text
SBI
State Bank
State Bank of India
SBI KYC Department
```

All can map to one organization.

## 13.3 Number lookup

The live raw caller number may remain only in RAM for lookup. Persist:

- match result;
- organization ID;
- source IDs;
- optionally a one-way hash if session correlation is required.

Do not persist the raw private number by default.

## 13.4 Domain lookup

Normalize domains by:

- lowercase;
- removing protocol;
- removing path;
- converting IDN safely where supported;
- removing trailing dot;
- validating shape.

Do not fetch a caller-provided domain during the call. Compare it only with the local trusted directory.

## 13.5 Policy contradictions

Examples:

```text
NO_OTP_REQUEST
NO_PIN_REQUEST
NO_CVV_REQUEST
NO_PASSWORD_REQUEST
NO_REMOTE_ACCESS
NO_SAFE_ACCOUNT_TRANSFER
NO_PAYMENT_TO_STOP_ARREST
```

A policy contradiction becomes an `IDENTITY` evidence event. It does not automatically prove fraud, but it can strongly increase risk through the risk engine.

## 13.6 Freshness

Every number, domain, and policy must have:

- source;
- verified date;
- expiry/review date;
- active flag.

Expired source handling:

```text
Do not return VERIFIED.
Return stale/insufficient status.
```

## 13.7 Safe result wording

Use:

> The number was not verified in the trusted directory. This alone does not prove fraud. End the call and verify through an independently obtained official channel.

Never use:

> This is definitely not SBI.

---

# 14. Phase 8 - Community Intelligence

## 14.1 Privacy-safe fingerprint

```python
class CampaignFingerprint(BaseModel):
    schema_version: int = 1
    tactic_codes: set[str]
    organization_type: str | None
    scenario_code: str | None
    requested_action_codes: set[str]
    threat_codes: set[str]
    payment_rail: str | None
    channel_switch: str | None
    language_family: str | None
    country_code: str = "IN"
```

Forbidden fields:

- raw audio;
- transcript;
- OTP;
- account values;
- private names;
- addresses;
- victim number;
- unrestricted private-text embedding.

## 14.2 Weight configuration

Store weights in exactly one file:

```python
DEFAULT_WEIGHTS = {
    "tactics": 0.25,
    "requested_actions": 0.25,
    "scenario": 0.15,
    "organization_type": 0.10,
    "threats": 0.10,
    "payment_rail": 0.05,
    "channel_switch": 0.05,
    "language_family": 0.05,
}
```

Validate that weights sum to `1.0`.

## 14.3 Weighted Jaccard

For set fields:

```text
J(A, B) = |A intersection B| / |A union B|
```

For scalar fields:

```text
match = 1 if equal and present
match = 0 if different
match = neutral/ignored if both absent, according to policy
```

Final:

```text
similarity = sum(weight[field] * component_score[field])
```

## 14.4 Output

```json
{
  "matched_pattern_id": "pattern_018",
  "similarity": 0.84,
  "campaign_code": "KYC_ACCOUNT_FREEZE",
  "component_scores": {
    "tactics": 0.75,
    "requested_actions": 1.0,
    "scenario": 1.0,
    "organization_type": 1.0,
    "threats": 1.0,
    "payment_rail": 0.0,
    "channel_switch": 0.0,
    "language_family": 1.0
  },
  "match_reasons": [
    "same requested action",
    "authority and urgency overlap",
    "same account-freeze threat"
  ],
  "data_source_code": "SYNTHETIC_PROTOTYPE_PATTERNS"
}
```

## 14.5 Interpretation

A high match means:

> Strong behavioral similarity to a known structured campaign pattern.

It does not mean:

> Confirmed scam.

Community evidence must have a limited score contribution and no independent critical override.

## 14.6 No ChromaDB

Do not add ChromaDB for the current prototype.

Future large-scale path:

```text
Structured filters
    ↓
Optional vector candidate retrieval
    ↓
Weighted structured reranking
```

---

# 15. Phase 9 - Model Bundles, Metrics, Evaluation, and Feedback

## 15.1 Model bundle purpose

Every session and evaluation must be reproducible.

A model bundle records:

- ASR model;
- embedding model or `NOT_USED`;
- classifier model;
- LLM model or `NOT_USED`;
- rule set;
- prompt;
- normalizer;
- risk policy;
- artifact manifest/hashes.

## 15.2 Development bundle

While models are unfinished, create:

```text
BUNDLE_DEV_UNRESOLVED
```

with explicit values such as:

```text
asr_model_id = NOT_SELECTED
classifier_model_id = NOT_SELECTED
llm_model_id = NOT_SELECTED
```

Do not invent a final model. Before the demo, insert a new immutable real bundle.

## 15.3 Metrics

Track at least:

- audio duration;
- ASR latency;
- fast rule/classifier latency;
- identity lookup latency;
- community match latency;
- database write latency;
- LLM latency;
- risk calculation latency;
- first warning latency;
- full decision latency;
- queue depth where available;
- database retry count;
- database failure count;
- cleanup duration.

## 15.4 Evaluation run

An evaluation run must record:

- dataset version;
- model bundle;
- commit hash;
- case counts;
- start/end timestamps;
- summary metrics;
- export path.

## 15.5 Required evaluation cases

1. bank KYC scam;
2. digital arrest;
3. UPI refund;
4. remote support;
5. courier/customs;
6. legitimate courier;
7. legitimate safety advice;
8. ambiguous OTP;
9. caller prompt injection;
10. LLM stopped;
11. database unavailable;
12. microphone unavailable;
13. noisy recording;
14. reset and cleanup.

## 15.6 CSV export

Minimum columns:

```text
evaluation_run_id
case_id
scenario
expected_label
actual_label
expected_min_risk
actual_max_risk
first_warning_ms
full_decision_ms
correct_evidence_count
false_evidence_count
database_status
privacy_pass
result
commit_hash
model_bundle_id
```

## 15.7 User feedback without frontend

Until the frontend exists, feedback can be supplied through:

```bash
python scripts/submit_feedback.py \
  --session S001 \
  --type FALSE_POSITIVE \
  --comment "Legitimate test scenario"
```

Later Palak's UI can call the same backend method.

---

# 16. Phase 10 - Cleanup and Retention Enforcement

## 16.1 End-session sequence

```text
1. Stop new audio input.
2. Flush final utterance if allowed.
3. Cancel stale tasks.
4. Mark session FINALIZED.
5. Clear audio ring buffer.
6. Clear unredacted transcript RAM.
7. Delete prohibited persisted utterances.
8. Retain only policy-allowed records.
9. Verify no private rows remain.
10. Mark session CLEARED.
11. Publish privacy status.
```

## 16.2 Cleanup must be idempotent

Calling cleanup twice should not crash or restore data.

## 16.3 Cleanup report

```json
{
  "session_id": "S001",
  "audio_buffer_cleared": true,
  "unredacted_state_cleared": true,
  "utterances_deleted": 12,
  "allowed_evidence_retained": 6,
  "allowed_risk_snapshots_retained": 4,
  "cleanup_verified": true,
  "completed_at_utc": "..."
}
```

## 16.4 Maximum privacy assertion

After cleanup:

```sql
SELECT COUNT(*) FROM utterances WHERE session_id = ?;
```

Expected:

```text
0
```

unless the user explicitly enabled permitted redacted transcript retention.

---

# 17. Phase 11 - Backup, Restore, and Corruption Safety

## 17.1 Backup rules

Use SQLite's backup API or a controlled checkpoint and copy. Do not copy an actively changing database file blindly.

Backup path:

```text
data/backups/suraksha_demo_YYYYMMDD_HHMMSS.db
```

## 17.2 Backup command

```bash
python -m app.database.backup
```

It should:

1. open source safely;
2. create destination directory;
3. use SQLite backup API;
4. run `PRAGMA integrity_check`;
5. verify expected tables;
6. write a backup manifest;
7. never include raw audio because raw audio is never in the database.

## 17.3 Restore test

A backup is not valid until a test restores it into a temporary directory and:

- opens the file;
- reads trusted organizations;
- reads patterns;
- verifies foreign keys;
- passes integrity check.

## 17.4 Corruption behavior

If integrity check fails:

- do not continue writing;
- report `DATABASE_CORRUPT`;
- continue active protection in memory;
- create a fresh safe database only through explicit recovery;
- keep the corrupt file for technical inspection if it contains only permitted test data.

---

# 18. Phase 12 - Optional Single Writer

## 18.1 Start without unnecessary complexity

First implement:

- WAL;
- busy timeout;
- short transactions;
- bounded retry.

Add a single writer only if concurrent write tests or the real backend produce lock problems.

## 18.2 Writer contract

```python
class DatabaseWriteCommand(BaseModel):
    command_id: str
    session_id: str | None
    operation: str
    payload: dict
    created_at_utc: str
```

## 18.3 Writer behavior

```text
Workers
   ↓
Bounded write queue
   ↓
Single writer task
   ↓
Repository/service call
   ↓
SQLite
```

Requirements:

- preserve command order per session;
- deduplicate command IDs;
- bounded retries;
- dead-letter metadata without private content;
- queue depth metric;
- graceful shutdown.

---

# 19. Mock Vertical Slice While Backend Is Incomplete

## 19.1 Purpose

The mock slice proves the entire database contract before real audio, AI, and UI are complete.

## 19.2 Mock scenario A - bank KYC scam

Create:

1. session;
2. three redacted utterances in evaluation mode;
3. authority evidence;
4. urgency evidence;
5. OTP-request evidence;
6. identity claim;
7. policy contradiction;
8. community pattern match;
9. risk snapshots `18 -> 48 -> 98`;
10. metrics;
11. evaluation feedback;
12. cleanup.

## 19.3 Mock scenario B - legitimate bank safety advice

Create:

- a sentence such as "Never share your OTP";
- `SAFE_ADVICE` evidence;
- no `SECRET_REQUEST`;
- low risk;
- no critical warning.

This prevents keyword-only design.

## 19.4 Script output

```bash
python scripts/run_mock_database_pipeline.py
```

Expected console summary:

```text
Database initialized: PASS
Seed idempotency: PASS
Scam scenario maximum risk: 98
Legitimate scenario maximum risk: 12
Identity policy contradiction: PASS
Community explanation: PASS
Maximum privacy cleanup: PASS
Evaluation CSV export: PASS
Browser-safe event scan: PASS
```

## 19.5 Mock integration completion

Mayank may mark a feature `MOCK_INTEGRATED` when:

- a fixture enters the repository/service;
- correct rows are written;
- expected rows can be read;
- outbound safe JSON is generated;
- cleanup and failure behavior are tested.

---

# 20. Backend Integration Plan When Ron's Work Is Ready

## 20.1 Integration boundary

Ron should receive a `DatabaseService` or repository bundle.

Example:

```python
class DatabaseService:
    sessions: SessionRepository
    utterances: UtteranceRepository
    evidence: EvidenceRepository
    risk: RiskRepository
    identity: IdentityRepository
    community: CommunityRepository
    models: ModelRepository
    feedback: FeedbackRepository
    evaluation: EvaluationRepository
```

## 20.2 Backend must not know table details

Good:

```python
await persistence.persist_detection_bundle(bundle)
```

Bad:

```python
conn.execute("INSERT INTO evidence_events ...")
```

## 20.3 Integration events

| Producer | Input to Mayank's layer | Database action |
|---|---|---|
| Odil | `TranscriptFinal` | Redact, policy-check, optionally persist utterance |
| Lakshay | `DetectionResult`, identity claim | Persist evidence/claim/result |
| Ron | Session lifecycle, agent outputs | Coordinate repository/service calls |
| Namit | `RiskDecision` | Persist risk snapshot and session maximum |
| Community service | `CampaignFingerprint` | Query patterns and store match |
| Palak/backend route | Feedback | Save feedback |
| QA runner | Metrics and expected values | Save metrics/evaluation |

## 20.4 Real integration tests

- Start session through backend.
- Persist a mock transcript through the actual route/event bus.
- Persist evidence and risk atomically.
- Disconnect database and verify warning still streams.
- End session and verify cleanup.
- Replay a full scenario.
- Export evaluation data.

---

# 21. Frontend Integration Plan When Palak's Work Is Ready

## 21.1 Frontend receives no SQL and no raw rows

The backend transforms repository data into UI events.

## 21.2 Stable outbound envelope

```json
{
  "type": "risk_update",
  "schema_version": 1,
  "message_id": "msg_001",
  "session_id": "S001",
  "sent_at_utc": "2026-07-27T10:00:00Z",
  "payload": {
    "risk_index": 91,
    "risk_band": "CRITICAL",
    "decision_code": "SCAM_LIKELY",
    "headline_code": "DO_NOT_TRANSFER",
    "reason_codes": [
      "AUTHORITY",
      "URGENT_PAYMENT_REQUEST",
      "IDENTITY_UNVERIFIED"
    ],
    "evidence_ids": ["E1", "E2", "E3"]
  }
}
```

## 21.3 Browser-safe fields

Allowed:

- redacted text;
- canonical codes;
- risk;
- evidence reason;
- verified/unverified state;
- safe action;
- latency/health indicators;
- privacy status.

Forbidden:

- raw transcript;
- raw phone number;
- OTP;
- account values;
- private metadata JSON;
- SQL errors;
- file paths;
- stack traces.

## 21.4 Reset event

```json
{
  "type": "session_cleared",
  "schema_version": 1,
  "session_id": "S001",
  "payload": {
    "transcript_visible": false,
    "private_state_cleared": true,
    "database_cleanup_verified": true
  }
}
```

## 21.5 Contract tests

Automated tests should scan fixture JSON for:

- OTP-like values;
- PAN;
- Aadhaar;
- account numbers;
- phone numbers;
- email;
- UPI;
- unredacted URLs;
- fields containing `raw_`.

---

# 22. Testing Strategy

## 22.1 Test database isolation

Each test must use:

- a temporary directory;
- a separate SQLite file;
- fresh schema;
- deterministic seed.

Never run automated tests against `data/database/suraksha.db`.

## 22.2 Schema tests

- all 18 application tables exist;
- foreign keys are on;
- WAL is on for file database;
- duplicate aliases are rejected;
- invalid risk is rejected;
- invalid confidence is rejected;
- invalid lifecycle is rejected;
- `audio_saved = 1` is rejected;
- orphan utterance is rejected;
- cascade behavior works;
- restricted source deletion works.

## 22.3 Repository tests

- session create/get/end/clear;
- duplicate session handling;
- maximum risk cannot decrease;
- utterance retention check;
- evidence insert and query;
- risk history ordering;
- alias lookup;
- number/domain lookup;
- policy lookup;
- claim/result persistence;
- pattern query and match;
- model bundle immutability;
- feedback persistence;
- metric and export.

## 22.4 Privacy tests

- raw audio table absent;
- `MAXIMUM_PRIVACY` blocks transcript persistence;
- OTP redacted;
- PAN redacted;
- Aadhaar redacted;
- account number redacted;
- phone redacted;
- UPI redacted;
- URL redacted;
- raw transcript absent from logs;
- community fingerprint has no private text;
- cleanup removes prohibited data;
- backup contains no prohibited fields.

## 22.5 Community tests

- identical fingerprint -> `1.0`;
- similar fingerprint -> expected medium/high range;
- unrelated fingerprint -> low range;
- empty fingerprint -> safe result;
- missing optional field -> no crash;
- weights sum to `1.0`;
- reasons match component scores;
- match is supporting evidence only.

## 22.6 Identity tests

- exact alias;
- abbreviation alias;
- unknown alias;
- known official number;
- unknown number;
- wrong organization number;
- known domain;
- suspicious domain;
- policy contradiction;
- expired source;
- missing source;
- unknown is never returned as confirmed scam.

## 22.7 Transaction tests

Inject a failure after evidence insert but before risk insert.

Expected:

```text
evidence row absent
risk row absent
session maximum unchanged
```

## 22.8 Failure tests

- file path unavailable;
- read-only database;
- database locked;
- constraint violation;
- corrupt database;
- backup failure;
- writer queue full;
- transient retry succeeds;
- persistent retry enters degraded mode.

## 22.9 Mock integration tests

- scam scenario produces critical history;
- legitimate safety advice remains low;
- database failure does not suppress warning event;
- cleanup produces `session_cleared`;
- event fixtures are browser-safe.

## 22.10 Test command

```bash
pytest backend/tests/database backend/tests/privacy \
       backend/tests/contracts backend/tests/integration -q
```

Add coverage if available:

```bash
pytest --cov=backend/app/database \
       --cov=backend/app/privacy \
       --cov=backend/app/community
```

---

# 23. Database Failure and Degraded Mode

## 23.1 Retry policy

Retry only transient errors:

- locked;
- busy;
- temporary I/O issue.

Do not retry indefinitely.

Example:

```text
attempt 1: immediate
attempt 2: 50 ms
attempt 3: 150 ms
attempt 4: 400 ms
then degraded mode
```

## 23.2 RAM fallback

When persistence fails:

- keep current risk and evidence in active state;
- emit warning;
- mark `persistence_enabled = false`;
- do not invent stored records;
- do not claim cleanup of rows that were never written;
- allow a later recovery event.

## 23.3 Recovery

When SQLite becomes available:

- health check;
- publish `RECOVERED`;
- do not automatically persist old raw transcript;
- optionally persist only still-allowed structured events;
- record a `SYSTEM` evidence/metric for outage duration.

## 23.4 Safe error event

```json
{
  "type": "system_status",
  "session_id": "S001",
  "payload": {
    "component": "DATABASE",
    "status": "DEGRADED",
    "warning_pipeline_active": true,
    "persistence_active": false,
    "error_code": "DB_LOCK_TIMEOUT"
  }
}
```

---

# 24. Data Dictionary Requirement

Create `docs/data-dictionary.md`.

For every field document:

| Field | Type | Nullable | Example | Privacy class | Producer | Consumer | Retention |
|---|---|---:|---|---|---|---|---|

Privacy classes:

```text
PUBLIC_REFERENCE
INTERNAL_TECHNICAL
REDACTED_CONVERSATION
ANONYMOUS_BEHAVIORAL
SENSITIVE_EPHEMERAL
PROHIBITED_PERSISTENCE
```

Examples:

- raw audio -> `PROHIBITED_PERSISTENCE`
- raw transcript -> `SENSITIVE_EPHEMERAL`
- redacted evidence -> `REDACTED_CONVERSATION`
- pattern tactic codes -> `ANONYMOUS_BEHAVIORAL`
- official organization name -> `PUBLIC_REFERENCE`

---

# 25. Required Developer Commands

```bash
# Initialize
python -m app.database.seed

# Reset controlled demo database
python -m app.database.seed --reset

# Inspect schema and row counts
python scripts/inspect_database.py

# Run database smoke test
python scripts/database_smoke_test.py

# Run the mock end-to-end persistence pipeline
python scripts/run_mock_database_pipeline.py

# Export evaluation
python scripts/export_evaluation.py --run <RUN_ID>

# Create verified backup
python scripts/backup_database.py

# Run tests
pytest backend/tests/database backend/tests/privacy \
       backend/tests/contracts backend/tests/integration -q
```

Every command must work from a documented project-root location.

---

# 26. Mayank's Detailed Implementation Order

## Phase A - Audit and freeze

1. Audit existing code.
2. Freeze naming.
3. Add status board.
4. Freeze contract models.
5. Freeze privacy rules.

**Exit:** The team agrees on tables, method names, and event shapes.

## Phase B - Foundation

6. Finalize `schema.sql`.
7. Finalize safe database path.
8. Enable foreign keys.
9. Enable WAL.
10. Add busy timeout.
11. Add transaction manager.
12. Add typed errors.
13. Add health check.

**Exit:** Empty database initializes and validates.

## Phase C - Core persistence

14. Complete session repository.
15. Complete utterance repository.
16. Complete evidence repository.
17. Complete risk repository.
18. Add atomic decision persistence service.
19. Add core tests.

**Exit:** Mock evidence and risk history persist atomically.

## Phase D - Trusted identity

20. Add trusted organizations.
21. Add aliases.
22. Add sources.
23. Add numbers.
24. Add domains.
25. Add policies.
26. Add identity claims.
27. Add verification results.
28. Add freshness and contradiction tests.

**Exit:** Known, unknown, expired, mismatch, and policy-contradiction cases work.

## Phase E - Community

29. Freeze fingerprint schema.
30. Freeze weights.
31. Complete matcher.
32. Complete repository/service.
33. Store explainable component scores.
34. Add privacy and similarity tests.

**Exit:** Similarity is deterministic, explainable, and private.

## Phase F - Privacy and cleanup

35. Complete redaction.
36. Complete retention policy.
37. Add final persistence validator.
38. Complete cleanup.
39. Add privacy status.
40. Add leakage tests.

**Exit:** Maximum-privacy cleanup is proven.

## Phase G - Reproducibility

41. Add model bundles.
42. Add user feedback.
43. Complete system metrics.
44. Complete evaluation runs.
45. Add CSV export.
46. Add test status documents.

**Exit:** One evaluation run can be reproduced and exported.

## Phase H - Reliability

47. Add indexes.
48. Add backup/restore.
49. Add bounded retries.
50. Add degraded mode.
51. Add optional writer only if needed.

**Exit:** Database failure cannot stop a warning.

## Phase I - Mock integration

52. Run scam scenario.
53. Run legitimate scenario.
54. Generate UI event fixtures.
55. Verify browser-safe output.
56. Run cleanup.
57. Export evaluation.

**Exit:** `MOCK_INTEGRATED`.

## Phase J - Real integration later

58. Integrate with Ron's state/event bus.
59. Integrate Lakshay's evidence/identity output.
60. Integrate Namit's RiskDecision.
61. Integrate Odil's TranscriptFinal.
62. Integrate Palak's frontend events.
63. Run replay pipeline.
64. Run live speakerphone pipeline.
65. Verify final laptop.

**Exit:** `DEMO_VERIFIED`.

---

# 27. Suggested 10-Day Personal Work Plan

This plan lets Mayank progress even when other modules are incomplete.

## Day 1 - Audit and contracts

- compare current schema with final 18-table design;
- create database status board;
- freeze IDs, enums, timestamps, and JSON contracts;
- create temporary test database fixture.

## Day 2 - Foundation

- finalize connection manager;
- enable foreign keys, WAL, busy timeout;
- implement transactions;
- implement health check;
- test initialization/reset.

## Day 3 - Core repositories

- sessions;
- utterances;
- evidence;
- risk;
- atomic decision bundle;
- core repository tests.

## Day 4 - Identity foundation

- organizations;
- aliases;
- numbers;
- domains;
- policies;
- sources;
- claims and verification;
- seed fixtures.

## Day 5 - Community foundation

- fingerprint validation;
- centralized weights;
- matcher;
- service;
- pattern matches;
- similarity and privacy tests.

## Day 6 - Privacy and cleanup

- ordered redaction;
- retention enforcement;
- persistence validator;
- cleanup;
- privacy status;
- leakage scan.

## Day 7 - Models and evaluation

- model bundles;
- feedback;
- metrics;
- evaluation run;
- CSV export.

## Day 8 - Reliability

- indexes;
- backup and restore;
- retry policy;
- degraded mode;
- database lock tests.

## Day 9 - Mock integration

- scam slice;
- legitimate slice;
- UI JSON fixtures;
- failure slice;
- cleanup slice;
- documentation.

## Day 10 - Handoff

- one-command smoke test;
- repository usage examples;
- contract handoff to Ron and Palak;
- final-laptop dry run when available;
- close critical defects only.

---

# 28. Cooperation With Other Members

## With Odil - audio and ASR

Mayank needs:

```text
utterance_id
session_id
sequence
speaker
started_ms
ended_ms
text
language
ASR confidence
ASR model ID
ASR latency
```

Agreement:

- Odil provides raw text only through in-memory/backend event.
- Mayank's privacy layer redacts before persistence.
- No audio is sent to SQLite.

## With Lakshay - dataset, rules, classifier, identity

Mayank provides:

- evidence repository contract;
- trusted directory lookup;
- alias resolver;
- official number/domain lookup;
- policy lookup;
- source provenance.

Lakshay provides:

- canonical labels;
- confidence;
- severity;
- source version;
- identity claim;
- requested action;
- expected evaluation labels.

## With Ron - backend/orchestration

Mayank provides:

- repository bundle;
- persistence service;
- transaction method;
- health/degraded events;
- mock event fixtures;
- no-SQL integration examples.

Ron provides:

- lifecycle events;
- canonical session state;
- event ordering;
- async integration location;
- shutdown hooks for cleanup.

## With Namit - team lead/risk

Mayank needs:

- final RiskDecision contract;
- component-score keys;
- risk policy version;
- evidence references;
- headline/action codes.

Mayank stores risk but does not calculate it.

## With Palak - frontend

Mayank provides:

- safe JSON fixture files;
- explicit null behavior;
- risk history shape;
- evidence timeline shape;
- identity wording codes;
- privacy and database status;
- clear/reset event.

Palak must never receive raw private fields.

---

# 29. Definition of Done

The database foundation is complete only when all of the following are true.

## Architecture

- [ ] SQLite is the only persistent application database.
- [ ] RAM is used for temporary live state.
- [ ] ChromaDB/PostgreSQL/Redis are not required for the demo.
- [ ] Frontend never accesses SQLite.
- [ ] Agents never write SQL directly.

## Schema

- [ ] All 18 application tables are implemented.
- [ ] Foreign keys work.
- [ ] CHECK constraints work.
- [ ] Unique constraints work.
- [ ] Required indexes exist.
- [ ] Raw audio storage is structurally prohibited.
- [ ] Raw caller number is not stored by default.

## Core persistence

- [ ] Session lifecycle works.
- [ ] Optional redacted utterance persistence works.
- [ ] Evidence persistence works.
- [ ] Risk history works.
- [ ] Atomic evidence-risk-session transactions work.

## Identity

- [ ] Organization aliases resolve.
- [ ] Official number lookup works.
- [ ] Official domain lookup works.
- [ ] Policies and sources work.
- [ ] Claims and verification results persist.
- [ ] Unknown is never treated as confirmed fraud.
- [ ] Expired sources do not return verified.

## Community

- [ ] Fingerprint contains no private text.
- [ ] Weighted Jaccard is centralized and tested.
- [ ] Pattern match stores component scores and reasons.
- [ ] Community match is supporting evidence only.

## Privacy

- [ ] Redaction occurs before persistence.
- [ ] Maximum-privacy transcript blocking works.
- [ ] Cleanup is idempotent.
- [ ] Privacy status is accurate.
- [ ] Logs and browser fixtures contain no private values.
- [ ] Backup contains only permitted data.

## Reproducibility

- [ ] Model bundles exist.
- [ ] Metrics persist.
- [ ] Evaluation runs persist.
- [ ] CSV export works.
- [ ] Feedback can be submitted through mock/CLI and later UI.
- [ ] Commit hash and model bundle are recorded.

## Reliability

- [ ] WAL is active.
- [ ] Busy timeout is active.
- [ ] Transactions roll back correctly.
- [ ] Database locks have bounded retries.
- [ ] Database failure enters RAM-only degraded mode.
- [ ] Warning delivery is not blocked by persistence failure.
- [ ] Backup restore is tested.
- [ ] Integrity check passes.

## Integration

- [ ] Mock vertical slice passes.
- [ ] Typed fixtures are delivered to Ron and Palak.
- [ ] Actual backend integration passes when ready.
- [ ] Actual frontend receives safe events when ready.
- [ ] Replay pipeline works.
- [ ] Final laptop test works.
- [ ] Another member can run the system from documentation.

---

# 30. Final Deliverables From Mayank

1. Final `schema.sql`.
2. Safe connection manager.
3. Transaction manager.
4. Complete repository classes.
5. Atomic persistence services.
6. Idempotent seed/reset.
7. Trusted organization seed data.
8. Reference source provenance.
9. Identity claim and verification persistence.
10. Community fingerprint and Weighted Jaccard service.
11. Pattern match explanations.
12. Redaction rules.
13. Retention policy.
14. Persistence privacy validator.
15. Cleanup service.
16. Privacy status.
17. Model bundle registry.
18. User feedback repository and CLI fixture.
19. Metrics repository.
20. Evaluation run and CSV export.
21. WAL and indexes.
22. Backup/restore.
23. Database health/degraded mode.
24. Mock end-to-end pipeline.
25. Browser-safe event fixtures.
26. Unit, privacy, identity, community, transaction, failure, and integration tests.
27. Data dictionary.
28. Database README.
29. Privacy and retention documents.
30. Test status and evaluation report.
31. Final-laptop verification report.

---

# 31. Judge Explanations

## Why SQLite?

> The prototype runs on one laptop and must remain local, offline, private, and reproducible. SQLite gives us relational constraints, transactions, indexes, WAL, backup, and simple deployment without a database server.

## Why no ChromaDB?

> Our community intelligence is a small structured fingerprint dataset. Weighted Jaccard is more explainable and sufficient for the prototype. A vector index becomes useful only when the corpus becomes large and semantic candidate retrieval is needed.

## What is stored?

> We store session metadata, redacted explainable evidence, risk history, trusted identity records, anonymous behavioral patterns, match reasons, model versions, and evaluation metrics.

## What is not stored?

> Raw call audio is never stored in SQLite. In maximum-privacy mode, unredacted transcript is also memory-only.

## Does an unknown number mean scam?

> No. It means unverified. The final risk decision combines behavior, dangerous requests, identity evidence, community similarity, and deterministic safety policy.

## What if the database fails?

> Detection and risk remain active in RAM. The warning still appears. Persistence enters a visible degraded mode and retries are bounded.

## How do you prove your result is reproducible?

> Each session and evaluation run references a model bundle containing ASR, classifier, LLM, rules, prompt, normalizer, and risk-policy versions, together with commit and evaluation metadata.

---

# 32. What Mayank Must Not Build Now

Do not spend the SIH window on:

- ChromaDB;
- PostgreSQL;
- pgvector;
- Redis;
- MongoDB;
- Kafka;
- NATS;
- cloud database;
- cloud audio storage;
- full production authentication;
- large-scale moderation platform;
- FTS5 unless evaluation search is actually needed;
- unrestricted transcript embeddings;
- automatic learning from user feedback;
- a separate `agent_results` table that duplicates evidence;
- complex Alembic infrastructure;
- production multi-tenant design;
- storing raw phone numbers for convenience.

---

# 33. Final Personal Checklist

- [ ] I audited the real code instead of trusting a documentation claim.
- [ ] My schema is the single source of truth.
- [ ] Every connection enables foreign keys.
- [ ] WAL and busy timeout are verified.
- [ ] Related writes are transactional.
- [ ] No agent writes SQL.
- [ ] The backend can integrate through repositories.
- [ ] The frontend can integrate through safe events.
- [ ] I can work without waiting for either frontend or backend.
- [ ] The mock vertical slice passes.
- [ ] No raw audio table exists.
- [ ] Raw transcript is never persisted in maximum privacy.
- [ ] Redaction is ordered and tested.
- [ ] Community fingerprints contain no private text.
- [ ] Unknown identity is not called fraud.
- [ ] Model versions are tracked.
- [ ] Metrics and evaluation export work.
- [ ] Cleanup is proven by queries.
- [ ] Database failure does not stop warnings.
- [ ] Backup restore is tested.
- [ ] Another team member can initialize and run the database.
- [ ] The final demonstration laptop passes the smoke test.

---

# 34. Final One-Line Responsibility

> Mayank builds SurakshaCall's complete privacy-safe system of record: a standalone, testable, local SQLite foundation that stores explainable session evidence, risk history, trusted identity intelligence, anonymous community patterns, versions, feedback, and evaluation data, while preventing raw audio and unnecessary private information from entering persistent storage.

---

# 35. Final Execution Rule

Do not wait for the frontend or backend.

Complete the database in this order:

```text
Schema
  ↓
Connection + WAL + transaction
  ↓
Repositories
  ↓
Seed/reset
  ↓
Privacy enforcement
  ↓
Identity foundation
  ↓
Community matching
  ↓
Model/evaluation/feedback
  ↓
Backup/failure handling
  ↓
Mock vertical slice
  ↓
Real backend integration
  ↓
Real frontend integration
  ↓
Final laptop verification
```

The database foundation is finished only when it is:

```text
secure
+ privacy-preserving
+ explainable
+ reproducible
+ mock-integrated
+ real-integrated
+ tested on the final demonstration laptop
```
