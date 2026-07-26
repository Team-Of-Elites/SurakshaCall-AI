# Ron — Multi-Agent Orchestration, FastAPI, WebSockets, and Real-Time Backend

> **Project:** SurakshaCall AI  
> **Member:** Ron  
> **Primary role:** Real-time backend and orchestration owner  
> **Secondary role:** Backup for local LLM integration and database APIs  
> **Main machine:** MacBook Air M3, 256 GB  
> **Success condition:** Every module communicates through one reliable, stateful, local backend without manual copying or hidden dependencies.

---

## 1. Your Mission

You are building the nervous system of SurakshaCall AI.

Odil will produce transcript events. Lakshay will produce fast detection and identity results. Mayank will provide persistence and community-pattern functions. Namit will provide the final Risk Decision. Palak will consume events in the interface.

Your backend must:

- create and end analysis sessions;
- keep recent conversation state;
- accept transcript events;
- trigger fast detection immediately;
- invoke deeper contextual analysis only when necessary;
- run identity and community lookups;
- request the final decision;
- broadcast validated events to laptop and phone interfaces;
- survive failure of optional components;
- remain easy to run completely locally.

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

1. FastAPI application structure;
2. backend configuration;
3. Pydantic event schemas;
4. session lifecycle;
5. WebSocket connection manager;
6. `CallState`;
7. `asyncio` event queues;
8. deterministic state graph or custom orchestrator;
9. deep-analysis trigger logic;
10. timeout, retry, and fallback behavior;
11. replay-session controller;
12. microphone-session controller;
13. local phone-dashboard connection;
14. health and diagnostics endpoint;
15. graceful startup and shutdown;
16. optional Docker packaging only after the local setup is stable.

You do not own the detailed UI, classifier training, audio signal processing, or risk weights. You do own the boundaries that let those modules work together.

## 3. Technologies You Must Learn

### Priority A

- FastAPI routers and lifespan;
- Pydantic v2;
- native WebSockets;
- `asyncio.Queue`;
- background task creation and cancellation;
- `asyncio.wait_for`;
- typed shared state;
- dependency injection;
- CORS for a local phone page;
- binding to `127.0.0.1` and a local network IP;
- structured logging;
- repository-service separation.

### Orchestration Choice

You may use LangGraph because it matches your skills, but keep routing deterministic.

Good use:

- typed state;
- conditional edges;
- parallel identity/community nodes;
- clear recovery paths.

Bad use:

- autonomous agents debating;
- recursive delegation;
- open-ended tool use;
- multiple large-model calls for every sentence.

A custom state machine is equally acceptable:

```text
Transcript received
    ↓
Fast detection
    ├── critical → immediate warning
    └── normal → decide whether deep analysis is due
                         ↓
                Context analysis
                  ↙          ↘
          Identity lookup   Community match
                  ↘          ↙
                  Final decision
                         ↓
                     Broadcast
```

### Learn Later Only If Needed

- Docker Compose;
- request tracing;
- SQLite checkpoints;
- simple performance profiling.

### Avoid

- Kafka;
- a message broker;
- mandatory Redis;
- distributed microservices;
- cloud-only deployment;
- a vector database in the critical path.

## 4. Folder Ownership

```text
backend/app/
├── main.py
├── config.py
├── lifespan.py
├── api/
│   ├── health.py
│   ├── sessions.py
│   ├── replay.py
│   └── mobile.py
├── websocket/
│   ├── manager.py
│   ├── dashboard.py
│   └── mobile.py
├── orchestration/
│   ├── graph.py
│   ├── routing.py
│   ├── state.py
│   └── worker.py
└── schemas/
    ├── events.py
    ├── transcript.py
    ├── evidence.py
    ├── identity.py
    └── decision.py
```

## 5. Task R-01 — Build the FastAPI Skeleton

Required endpoints:

```text
GET  /api/health
POST /api/sessions
GET  /api/sessions/{session_id}
POST /api/sessions/{session_id}/start-microphone
POST /api/sessions/{session_id}/start-replay
POST /api/sessions/{session_id}/end
POST /api/sessions/{session_id}/reset
POST /api/sessions/{session_id}/caller-metadata
WS   /ws/dashboard/{session_id}
WS   /ws/mobile/{session_id}
```

### How to Do It

1. Create an application factory.
2. Load settings from `.env`.
3. Initialize database access in the lifespan handler.
4. Initialize model clients without blocking startup forever.
5. Register routers.
6. Add CORS only for known local development origins.
7. Add graceful shutdown that cancels workers and clears session buffers.
8. Keep a configuration switch for laptop-only versus local-network mode.

### Acceptance Criteria

- `/api/health` works even if the local language model is stopped;
- sessions can be created, read, reset, and ended;
- dashboard WebSocket connects;
- mobile WebSocket connects from the same hotspot;
- shutdown leaves no running audio or analysis tasks.

## 6. Task R-02 — Freeze the Shared Event Envelope

```python
from datetime import datetime
from pydantic import BaseModel

class EventEnvelope(BaseModel):
    type: str
    session_id: str
    timestamp: datetime
    payload: dict
```

Required event types:

```text
session_started
session_snapshot
session_reset
audio_status
transcript_partial
transcript_final
fast_detection
tactic_detected
identity_claimed
identity_verified
community_match
risk_update
safety_warning
privacy_status
system_status
system_error
session_ended
```

### Event Rules

- every event carries a session ID;
- every final utterance has an utterance ID;
- every evidence item has an evidence ID;
- do not publish Python stack traces to the UI;
- preserve event order per session;
- malformed internal events are rejected before broadcast;
- use timezone-aware timestamps consistently.

## 7. Task R-03 — Build Call State

```python
class CallState(BaseModel):
    session_id: str
    caller_number: str | None = None
    started_at: datetime
    input_mode: Literal["microphone", "replay"]
    transcript_window: list[Utterance] = []
    previous_summary: str = ""
    evidence_events: list[EvidenceEvent] = []
    claimed_identities: list[IdentityClaim] = []
    verification_results: list[VerificationResult] = []
    community_matches: list[CommunityMatch] = []
    current_risk: int = 0
    current_level: str = "LOW"
    risk_history: list[RiskSnapshot] = []
    last_deep_analysis_at: datetime | None = None
    words_since_analysis: int = 0
    llm_available: bool = True
```

### State Rules

- retain the latest 60–120 seconds of transcript;
- summarize older safe context;
- never discard active critical evidence during the session;
- isolate each session;
- clear unredacted text at end;
- support a clean reset for repeated demonstrations;
- store speaker as `unknown` when the microphone mix cannot separate participants.

## 8. Task R-04 — Build the Queue-Based Pipeline

Recommended flow:

```text
Odil audio worker
    ↓
transcript_final queue
    ↓
Lakshay fast detector
    ↓
Ron orchestrator
    ├── immediate critical broadcast
    └── optional deep analysis
              ↓
       identity/community
              ↓
        Namit decision
              ↓
    dashboard/mobile broadcast
```

### Important Rules

- Whisper must not wait for the language model;
- critical rules publish before deep analysis;
- slow work runs outside the audio callback;
- avoid two overlapping deep analyses on unchanged context;
- cancel workers when a session ends;
- cap queue growth;
- finalized utterances must not be silently dropped.

## 9. Task R-05 — Deep-Analysis Triggering

Invoke deeper analysis when:

- a critical rule fires;
- fast risk exceeds 25;
- two manipulation labels appear within 30 seconds;
- an organization claim appears;
- payment, credential, remote access, or isolation appears;
- 8–12 seconds pass during active speech;
- at least 12 new words exist;
- the user presses “Analyze now.”

Configuration:

```yaml
normal_interval_seconds: 10
high_risk_interval_seconds: 4
minimum_new_words: 12
critical_immediate: true
llm_timeout_seconds: 6
structured_retry_count: 1
```

## 10. Task R-06 — Implement the State Graph

Suggested nodes:

```text
ingest_transcript
normalize_state
run_fast_detection
publish_fast_events
check_deep_trigger
analyze_context
extract_identity
verify_identity
match_community
aggregate_decision
publish_final_events
```

### Parallel Work

Run identity and community nodes together when possible:

```python
identity, community = await asyncio.gather(
    verify_identity(state),
    match_community(state),
    return_exceptions=True,
)
```

Convert an exception into an `INSUFFICIENT_DATA` result rather than crashing the session.

## 11. Task R-07 — WebSocket Manager

The manager must:

- accept dashboard and mobile clients;
- group by session;
- broadcast validated events;
- remove disconnected clients;
- reconnect with current snapshot;
- use a local session token;
- limit payload size;
- prevent one slow client from blocking all clients.

Reconnect snapshot example:

```json
{
  "type": "session_snapshot",
  "payload": {
    "current_risk": 72,
    "risk_level": "CRITICAL",
    "recent_transcript": [],
    "evidence_events": [],
    "privacy_status": {}
  }
}
```

## 12. Task R-08 — Replay Controller

Replay is mandatory.

Requirements:

- accept only files from `data/demo/`;
- validate WAV input;
- preserve natural timing;
- feed Odil’s same audio queue;
- support stop and reset;
- publish progress;
- never bypass VAD, Whisper, or detection.

Request:

```json
{
  "file_name": "bank_kyc_hi_en.wav",
  "speed": 1.0
}
```

Reject arbitrary paths.

## 13. Task R-09 — Local Phone Connection

The mobile page can open:

```text
http://LAPTOP_LOCAL_IP:5173/mobile/{session_id}
```

Backend:

```text
http://LAPTOP_LOCAL_IP:8000
ws://LAPTOP_LOCAL_IP:8000/ws/mobile/{session_id}
```

Reliability steps:

1. Use a team hotspot if college Wi-Fi blocks peer devices.
2. Configure firewall before the event.
3. Display a QR code for the mobile URL.
4. Keep laptop-only mode ready.
5. Treat caller-number metadata as manual or user-provided unless a reliable local source exists.

## 14. Task R-10 — Health and Diagnostics

```json
{
  "backend": "ok",
  "database": "ok",
  "whisper": "ready",
  "local_llm": "ready",
  "microphone": "ready",
  "active_sessions": 1,
  "mode": "local"
}
```

Failure policy:

| Failure | Behavior |
|---|---|
| LLM timeout | rules-only mode continues |
| Database error | memory-only mode |
| Mobile disconnected | laptop dashboard continues |
| Microphone error | offer replay |
| Malformed event | reject and log redacted error |
| Session end | cancel tasks and clear buffers |
| Frontend reconnect | send current snapshot |

## 15. Cooperation

### With Namit

- freeze the decision schema;
- define model timeout;
- agree on state sent to contextual analysis;
- verify rules-only fallback.

### With Odil

- agree on `AudioFrame` and `TranscriptFinal`;
- define cancellation;
- keep audio processing outside orchestration.

### With Lakshay

- expose one detector service;
- keep labels stable;
- integrate identity lookup.

### With Mayank

- use repository interfaces;
- support memory fallback;
- avoid persistence in the time-critical warning path.

### With Palak

- provide mock fixtures;
- test reconnect;
- test local mobile URL;
- agree on friendly system-error wording.

## 16. Day-by-Day Work

### Day 1
- FastAPI skeleton;
- event schemas;
- health endpoint;
- WebSocket manager.

### Day 2
- replay transcript to detector to risk to dashboard.

### Day 3
- CallState, queues, cooldown.

### Day 4
- local LLM node, timeout, schema repair.

### Day 5
- stabilize scam and legitimate paths.

### Day 6
- microphone session and local phone page.

### Day 7
- identity/community parallel nodes.

### Day 8
- final-machine migration.

### Day 9
- latency instrumentation.

### Day 10
- offline and component-failure testing.

### Day 11
- architecture documentation.

### Day 12
- rehearsal support.

### Days 13–14
- critical fixes, final commands, archive.

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

## 17. Required Tests

```text
create/end session
session isolation
event validation
WebSocket broadcast
reconnect snapshot
fast warning before LLM
deep-analysis cooldown
LLM timeout fallback
database failure memory mode
replay path restriction
session reset
shutdown clears workers
local mobile client reconnect
```

## 18. Final Deliverables

- FastAPI application;
- typed schemas;
- session state;
- queues;
- orchestration graph;
- WebSocket manager;
- replay controller;
- microphone-session control;
- local phone connection;
- health diagnostics;
- fallback logic;
- API documentation;
- start and stop instructions.

## 19. Judge Questions

### Why multi-agent with one local model?

> Agents are specialized responsibilities and tool boundaries. Manipulation, identity, community, and decision components use different inputs and schemas but may share one local model for speed.

### Why a graph?

> A graph makes safety and latency predictable. Critical rules run first; slower contextual analysis runs conditionally.

### What if a component fails?

> Rules continue without the language model, memory state continues without the database, and the laptop interface continues without the phone page.

## 20. First 24 Hours

- create backend;
- define event envelope;
- implement health;
- implement session create/end;
- create dashboard WebSocket;
- accept mock transcript;
- broadcast mock risk;
- document commands.

## 21. Personal Checklist

- [ ] Sessions are isolated.
- [ ] Events are typed.
- [ ] Critical warnings are not blocked.
- [ ] Timeouts exist.
- [ ] Database failure is survivable.
- [ ] WebSockets reconnect.
- [ ] Replay uses the real pipeline.
- [ ] Phone page is optional.
- [ ] Shutdown clears workers.
- [ ] API is documented.

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
