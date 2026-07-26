# Mayank — Database, Community Intelligence, Privacy Persistence, Frontend Data Integration, and QA

> **Project:** SurakshaCall AI  
> **Member:** Mayank  
> **Primary role:** Structured data, community matching, privacy-safe persistence, and QA  
> **Secondary role:** Frontend event handling and trusted-directory backup  
> **Main machine:** Asus F15, 16 GB RAM, RTX 2050, 512 GB  
> **Success condition:** The system stores only necessary redacted data, retrieves explainable intelligence, clears private state, and passes repeatable regression tests.

---

## 1. Your Mission

You make the project reproducible and privacy-safe.

Your system must answer:

- what evidence occurred;
- how risk changed;
- whether identity was verified;
- whether a similar anonymous pattern exists;
- what was stored;
- whether private data was cleared;
- whether the current version passed tests.

## Project Architecture Used in This Role Guide

This role guide assumes a **fully local hackathon prototype**. No external call-routing or cloud telephony service is used.

### Primary live demonstration

```text
Test Caller Phone
        |
        | normal cellular call
        v
Victim/Test Phone on speaker mode
        |
        | acoustic conversation
        v
Laptop microphone
        |
        v
Local audio capture and Voice Activity Detection
        |
        v
faster-whisper speech recognition
        |
        v
Fast safety rules and lightweight classifier
        |
        v
Multi-agent contextual analysis
        |
        v
Deterministic Risk Index and explanation
        |
        v
Laptop dashboard and optional phone warning page
```

The laptop microphone hears both people because the victim phone is placed on speaker. This is a prototype technique, not unrestricted interception of cellular-call audio.

### Mandatory backup demonstration

```text
Prerecorded WAV conversation
        |
        | replayed in real time
        v
The same VAD, Whisper, detection, agent, risk, and UI pipeline
```

The replay mode must not bypass the real pipeline. It should feed audio in timed chunks so the transcript and Risk Index change progressively.

### Optional phone-to-laptop connection

The phone may connect to the laptop through:

- the same local Wi-Fi network;
- a mobile hotspot;
- USB with Android Debug Bridge port forwarding;
- a mobile browser page opened from the laptop's local IP.

This connection is for:

- starting or ending a protection session;
- manually entering or sending the caller number when available;
- showing the warning on the phone;
- showing connection and privacy status.

It is **not** treated as a reliable source of both sides of cellular-call audio.

### Privacy wording

The prototype should state:

> Conversation audio is captured by the local laptop microphone or played from a consented test recording. Raw audio is held only in a short in-memory buffer and is not saved by default. Speech recognition and scam analysis run locally on the demonstration laptop.

The team must not claim that it has built a universal phone-call interceptor. The prototype demonstrates the intelligence pipeline and a realistic local integration path.

## 2. Exact Ownership

You own:

1. SQLite schema;
2. database initialization;
3. repository functions;
4. session metadata;
5. optional redacted utterances;
6. evidence;
7. risk snapshots;
8. trusted-directory persistence;
9. community patterns;
10. transparent similarity;
11. retention and deletion;
12. privacy events;
13. QA status;
14. regression coordination;
15. evaluation runs;
16. frontend data integration;
17. issue triage support.

## 3. Technologies to Learn

### Must Learn

- SQLite;
- foreign keys;
- indexes;
- transactions;
- Python `sqlite3` or SQLAlchemy;
- repository pattern;
- JSON serialization;
- redaction;
- retention;
- weighted Jaccard;
- pytest integration tests;
- TypeScript event types;
- issue tracking.

Use SQLite because it is local, simple, offline, and enough.

### Later Only If Needed

- Alembic;
- PostgreSQL;
- vector matching;
- database encryption.

### Avoid

- multiple databases;
- raw audio storage;
- full unredacted transcript by default;
- private embeddings;
- community data treated as truth;
- vector database for a tiny dataset.

## 4. Folder Ownership

```text
backend/app/database/
├── connection.py
├── schema.sql
├── seed.py
├── repositories.py
└── cleanup.py

backend/app/community/
├── fingerprint.py
├── matcher.py
├── weights.py
└── service.py

backend/app/privacy/
├── redaction.py
├── retention.py
└── status.py

data/trusted_directory/
data/community_patterns/
data/evaluation/
docs/privacy.md
docs/test-status.md
docs/data-dictionary.md
docs/evaluation.md
```

## 5. Task M-01 — SQLite Schema

Tables:

```text
sessions
utterances
evidence_events
risk_snapshots
trusted_organizations
official_numbers
verification_results
community_patterns
community_matches
system_metrics
evaluation_runs
```

Example:

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    input_mode TEXT NOT NULL,
    caller_number_redacted TEXT,
    transcript_retention_enabled INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL
);
```

Utterances are saved only when enabled and redacted.

Evidence and risk tables store structured data.

## 6. Task M-02 — Initialization and Seed

Command:

```bash
python -m app.database.seed
```

It should:

1. create directory;
2. enable foreign keys;
3. execute schema;
4. insert trusted organizations;
5. insert synthetic patterns;
6. insert demo scenarios;
7. be idempotent.

Reset:

```bash
python -m app.database.seed --reset
```

## 7. Task M-03 — Repository Layer

Functions:

```python
create_session(...)
get_session(...)
end_session(...)
add_redacted_utterance(...)
add_evidence_event(...)
add_risk_snapshot(...)
find_organization_by_alias(...)
find_official_number(...)
add_verification_result(...)
find_similar_patterns(...)
add_community_match(...)
save_metric(...)
clear_session_private_data(...)
```

Rules:

- no SQL in orchestration;
- parameterized queries;
- transactions;
- typed returns;
- database errors handled;
- safety continues in memory.

## 8. Task M-04 — Redaction

Redact before persistence:

- OTP-like codes;
- card/account numbers;
- Aadhaar-like numbers;
- email;
- UPI ID;
- URL;
- phone;
- names only when reliable.

Example:

```text
Raw:
My OTP is 482193 and account is 123456789012.

Saved:
My [OTP_REDACTED] and account is [ACCOUNT_REDACTED].
```

Preserve semantic evidence.

## 9. Task M-05 — Retention Modes

Maximum privacy:

```text
Raw audio: memory only
Transcript: memory only
Evidence/risk: session only
```

Demo evaluation:

```text
Known test audio file
Redacted test transcript
Evidence and metrics saved
```

End sequence:

1. stop audio;
2. cancel tasks;
3. clear ring buffer;
4. clear unredacted state;
5. optionally save redacted report;
6. publish privacy status;
7. verify cleanup.

## 10. Task M-06 — Community Fingerprint

```json
{
  "schema_version": 1,
  "tactics": ["AUTHORITY", "URGENCY", "ISOLATION"],
  "organization_type": "BANK",
  "scenario": "BANK_KYC",
  "requested_action": "SECRET_CODE",
  "threat_type": "ACCOUNT_FREEZE",
  "channel_switch": "NONE",
  "language_family": "HI_EN"
}
```

Never include raw audio, full transcript, secret, victim number, name, address, contacts, or unrestricted embeddings.

## 11. Task M-07 — Weighted Similarity

Weights:

| Field | Weight |
|---|---:|
| Requested action | 4 |
| Tactics | 3 |
| Scenario | 3 |
| Threat type | 2 |
| Organization type | 2 |
| Channel switch | 1 |
| Language | 1 |

Output:

```json
{
  "matched_pattern_id": "pattern_018",
  "similarity": 0.84,
  "campaign_label": "KYC_ACCOUNT_FREEZE",
  "match_reasons": [
    "same requested action",
    "authority and urgency overlap",
    "same threat type"
  ],
  "data_source": "synthetic_prototype_patterns"
}
```

A match is supporting evidence, not proof.

## 12. Task M-08 — Trusted Directory Persistence

Persist Lakshay's records.

Functions:

```python
find_organization_by_alias(name)
find_number(number)
get_never_request_policies(org_id)
```

Statuses:

```text
VERIFIED
UNVERIFIED
NOT_IN_DIRECTORY
INSUFFICIENT_DATA
```

Never return fraud from lookup alone.

## 13. Task M-09 — Frontend Integration

Provide stable event examples. Ensure:

- nulls are explicit;
- enums stable;
- dates strings;
- private raw fields never reach browser;
- reset removes transcript.

## 14. Task M-10 — QA Board

`docs/test-status.md`:

```text
Scenario:
Commit:
Date:
Input mode:
Whisper model:
Local LLM:
Expected risk:
Actual risk:
Fast warning latency:
Full decision latency:
Correct evidence:
False evidence:
Result:
Open issue:
Owner:
```

## 15. Task M-11 — Regression Suite

Cases:

1. bank KYC;
2. digital arrest;
3. UPI refund;
4. remote support;
5. courier/customs;
6. legitimate courier;
7. legitimate safety advice;
8. ambiguous OTP;
9. prompt injection;
10. LLM stopped;
11. database unavailable;
12. microphone unavailable;
13. noisy recording;
14. reset/cleanup.

## 16. Task M-12 — Metrics

Store:

- audio duration;
- transcript latency;
- fast warning latency;
- full latency;
- expected/actual labels;
- expected/actual risk;
- model versions;
- commit hash.

Export:

```text
data/evaluation/latest_results.csv
```

## 17. Task M-13 — Failure and Cleanup

Database unavailable:

- memory mode;
- warning continues;
- UI status;
- no crash.

Session cleanup:

- no audio buffer;
- no unredacted transcript;
- ended status;
- optional redacted report only.

Seed/reset must recover demo.

## 18. Cooperation

- Lakshay: trusted data and evaluation.
- Ron: repositories and memory fallback.
- Namit: score contribution and privacy wording.
- Palak: data types and reset.
- Odil: no raw persistence and timing.

## 19. Day-by-Day Work

### Day 1
- schema;
- connection;
- QA template.

### Day 2
- session/risk persistence;
- first integration.

### Day 3
- evidence and trusted tables.

### Day 4
- repositories and aliases.

### Day 5
- replay regression data.

### Day 6
- redaction/privacy.

### Day 7
- community matcher.

### Day 8
- final-machine seed/reset.

### Day 9
- evaluation coordination.

### Day 10
- failure and cleanup.

### Day 11
- privacy/community presentation.

### Day 12
- rehearsal defects.

### Days 13–14
- close critical issues;
- export results.

## Shared 14-Day Milestones

| Day | Team milestone |
|---|---|
| 1 | Repository, schemas, mock dashboard, first audio and rule tests |
| 2 | Replay audio → transcript → critical rule → risk warning → dashboard |
| 3 | VAD, expanded rules, conversation state, database |
| 4 | Structured local LLM analysis and first classifier |
| 5 | Stable replay integration with scam and legitimate scenarios |
| 6 | Live speakerphone/microphone test and local phone connection |
| 7 | Identity verification and community-pattern matching |
| 8 | Full system migrated to Namit's final laptop |
| 9 | Held-out evaluation and latency measurement |
| 10 | Privacy, failure, and offline testing |
| 11 | Interface polish and presentation material |
| 12 | Five full rehearsals and backup recording |
| 13 | Critical bug fixes only |
| 14 | Release freeze, archive, and final rehearsal |

## 20. Required Tests

```text
seed idempotent
foreign keys
parameterized queries
session create/end
evidence
risk snapshot
OTP redaction
account redaction
no raw audio table
community similarity
identity lookup
database failure
clear private data
evaluation export
no private browser fields
```

## 21. Final Deliverables

- schema;
- seed/reset;
- repositories;
- redaction;
- retention;
- community fingerprint;
- matcher;
- trusted persistence;
- privacy status;
- QA board;
- regression results;
- evaluation CSV;
- cleanup tests;
- privacy documentation.

## 22. Judge Questions

### What is shared in community intelligence?

> Only structured behavior categories such as authority, urgency, threat, and requested action. Not raw audio or full private conversation.

### Is a match proof?

> No. It is limited supporting evidence.

### What happens after a session?

> Raw audio is not saved by default. Active transcript is cleared, and only optional redacted test data is retained in evaluation mode.

## 23. First 24 Hours

- create schema;
- connect database;
- seed one organization and five patterns;
- session/risk repository;
- QA template;
- privacy mode agreement;
- mock community event for Palak.

## 24. Personal Checklist

- [ ] Reliable SQLite.
- [ ] Typed repository.
- [ ] No raw audio.
- [ ] Redaction before persistence.
- [ ] Cleanup tested.
- [ ] Fingerprint has no private text.
- [ ] Similarity explainable.
- [ ] Unknown not fraud.
- [ ] Database failure survivable.
- [ ] Reproducible evaluation.
- [ ] Offline reset works.

## Team-Wide Working Rules

1. The `main` branch must remain demoable.
2. The replay-based end-to-end pipeline must work by Day 2.
3. Every feature must expose a typed input and output.
4. Every task must include at least one test.
5. No finished module may remain only inside a notebook.
6. Interface changes require agreement from the affected members.
7. Local and private processing is the default.
8. Raw audio must not be committed, logged, or saved unintentionally.
9. A large language model may add context but may not remove deterministic critical warnings.
10. Optional features must never break the core demonstration.
11. Each member must maintain a short `README` for their module.
12. Every evening the team must run one scam case, one legitimate case, and one failure case.

### Shared event flow

```text
Odil: AudioFrame / TranscriptFinal
        |
        v
Lakshay: DetectionResult / IdentityLookup
        |
        v
Ron: CallState / Agent orchestration
        |
        v
Namit: RiskDecision
        |
        v
Mayank: persistence, community match, testing
        |
        v
Palak: dashboard and mobile warning
```

### Shared definition of done

A task is complete only when:

- the code is committed;
- another member can run it;
- setup instructions exist;
- input and output are documented;
- a test exists;
- errors are handled;
- it works in the integrated branch;
- it works on the final demonstration laptop when relevant;
- it does not expose secrets or private data.
