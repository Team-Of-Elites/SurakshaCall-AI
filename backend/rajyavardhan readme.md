# Rajyavardhan — Multi Agent AI Orchestration, FastAPI, WebSockets, and Real Time Backend

> **Project:** SurakshaCall AI
> **Member:** Rajyavardhan
> **Primary role:** Real time backend and orchestration owner
> **Secondary role:** Backup for local LLM integration and database APIs
> **Main machine:** MacBook Air M3, 256 GB
> **Success condition:** Every module communicates through one reliable, stateful, local backend without manual copying or hidden dependencies.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [My Mission](#2-my-mission)
3. [Project Architecture](#3-project-architecture)
4. [Exact Ownership](#4-exact-ownership)
5. [Technologies I Must Learn](#5-technologies-i-must-learn)
6. [Folder Ownership](#6-folder-ownership)
7. [Task R01 — FastAPI Skeleton](#7-task-r01--fastapi-skeleton)
8. [Task R02 — Shared Event Envelope](#8-task-r02--shared-event-envelope)
9. [Task R03 — Call State](#9-task-r03--call-state)
10. [Task R04 — Queue Based Pipeline](#10-task-r04--queue-based-pipeline)
11. [Task R05 — Deep Analysis Triggering](#11-task-r05--deep-analysis-triggering)
12. [Task R06 — State Graph](#12-task-r06--state-graph)
13. [Task R07 — WebSocket Manager](#13-task-r07--websocket-manager)
14. [Task R08 — Replay Controller](#14-task-r08--replay-controller)
15. [Task R09 — Local Phone Connection](#15-task-r09--local-phone-connection)
16. [Task R10 — Health and Diagnostics](#16-task-r10--health-and-diagnostics)
17. [Extension — Phone Microphone Streaming](#17-extension--phone-microphone-streaming)
18. [Cooperation With the Team](#18-cooperation-with-the-team)
19. [Day by Day Work](#19-day-by-day-work)
20. [Shared 14 Day Milestones](#20-shared-14-day-milestones)
21. [Required Tests](#21-required-tests)
22. [Final Deliverables](#22-final-deliverables)
23. [Judge Questions](#23-judge-questions)
24. [First 24 Hours](#24-first-24-hours)
25. [Personal Checklist](#25-personal-checklist)
26. [Team Wide Working Rules](#26-team-wide-working-rules)
27. [Shared Event Flow](#27-shared-event-flow)
28. [Definition of Done](#28-definition-of-done)
29. [Local Setup and Run Instructions](#29-local-setup-and-run-instructions)
30. [Closing Note](#30-closing-note)

---

## 1. Project Overview

SurakshaCall AI is a fully local, privacy first scam call protection prototype. It listens to a live phone conversation, transcribes it in real time, reasons about manipulation tactics, verifies claimed identities, checks community reported patterns, and produces a single deterministic Risk Index that is broadcast to a dashboard and, optionally, to a phone.

Nothing about this system depends on cloud telephony, call interception at the carrier level, or any external inference API. Every model, every queue, and every decision runs on the demonstration laptop itself. That single constraint, everything local, everything explainable, everything reproducible, shapes every design decision documented in this file.

The team is split across six roles. Odil owns audio capture and speech recognition. Lakshay owns fast rule based detection and identity signals. Mayank owns persistence and community pattern matching. Namit owns the final risk decision logic. Palak owns the dashboard and mobile interface. I own the backend that ties all five of these together, plus the orchestration graph that decides when and in what order their work runs.

This README documents my role end to end: what I am responsible for, what I am explicitly not responsible for, the technologies I need to be fluent in, the folder structure I own, every task assigned to me with acceptance criteria, the schemas I am required to freeze early so other members can build against them, the day by day plan, and the additional phone microphone streaming feature I built beyond the original scope, which lets a phone's own microphone stream live audio into this backend over a WebSocket instead of relying only on a laptop microphone.

## 2. My Mission

I am building the nervous system of SurakshaCall AI.

Odil produces transcript events. Lakshay produces fast detection and identity results. Mayank provides persistence and community pattern functions. Namit provides the final Risk Decision. Palak consumes events in the interface.

My backend must:

- create and end analysis sessions
- keep recent conversation state
- accept transcript events
- trigger fast detection immediately
- invoke deeper contextual analysis only when necessary
- run identity and community lookups
- request the final decision
- broadcast validated events to laptop and phone interfaces
- survive failure of optional components
- remain easy to run completely locally

I do not own the detailed UI, classifier training, audio signal processing, or risk weights. I do own the boundaries that let those modules work together correctly, in order, and without silently losing data.

## 3. Project Architecture

This role guide assumes a fully local hackathon prototype. No external call routing or cloud telephony service is used anywhere in this system.

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
Multi agent contextual analysis
        |
        v
Deterministic Risk Index and explanation
        |
        v
Laptop dashboard and optional phone warning page
```

The laptop microphone hears both people because the victim phone is placed on speaker. This is a prototype technique, not unrestricted interception of cellular call audio. No mobile platform allows a third party application unrestricted access to both sides of a live cellular call, and this project does not attempt to claim otherwise.

### Mandatory backup demonstration

```text
Prerecorded WAV conversation
        |
        | replayed in real time
        v
The same VAD, Whisper, detection, agent, risk, and UI pipeline
```

The replay mode must never bypass the real pipeline. It feeds audio in timed chunks so the transcript and Risk Index change progressively, exactly as they would during a live call. This exists because live demos can fail for reasons entirely outside our control, venue WiFi, a call that does not connect, background noise. The replay path is the fallback that guarantees the judges see the actual pipeline working end to end regardless of what happens with live audio on the day.

### Optional phone to laptop connection

The phone may connect to the laptop through:

- the same local WiFi network
- a mobile hotspot
- USB with Android Debug Bridge port forwarding
- a mobile browser page opened from the laptop's local IP

This connection is for:

- starting or ending a protection session
- manually entering or sending the caller number when available
- showing the warning on the phone
- showing connection and privacy status
- as of my extension work described in section 17, streaming live microphone audio from the phone itself into the backend

It is not treated as the only reliable source of both sides of cellular call audio. The laptop microphone path remains the primary, always working fallback.

### Privacy wording

The prototype states, plainly, to judges and anyone else who asks:

> Conversation audio is captured by the local laptop microphone, the phone's own microphone streamed over the local network, or played from a consented test recording. Raw audio is held only in a short in memory buffer and is not saved by default. Speech recognition and scam analysis run locally on the demonstration laptop.

The team must not claim to have built a universal phone call interceptor. The prototype demonstrates the intelligence pipeline and a realistic local integration path, nothing more, and that is a deliberately honest and defensible claim to make in front of judges.

## 4. Exact Ownership

I own:

1. FastAPI application structure
2. backend configuration
3. Pydantic event schemas
4. session lifecycle
5. WebSocket connection manager
6. `CallState`
7. `asyncio` event queues
8. deterministic state graph or custom orchestrator
9. deep analysis trigger logic
10. timeout, retry, and fallback behavior
11. replay session controller
12. microphone session controller
13. local phone dashboard connection
14. health and diagnostics endpoint
15. graceful startup and shutdown
16. optional Docker packaging only after the local setup is stable
17. the phone microphone streaming extension, mobile pairing, and QR based session handoff

I do not own the detailed UI, classifier training, audio signal processing, or risk weights. I do own the boundaries that let those modules work together.

## 5. Technologies I Must Learn

### Priority A

- FastAPI routers and lifespan
- Pydantic v2
- native WebSockets
- `asyncio.Queue`
- background task creation and cancellation
- `asyncio.wait_for`
- typed shared state
- dependency injection
- CORS for a local phone page
- binding to `127.0.0.1` and a local network IP
- structured logging
- repository service separation

### Orchestration Choice

I may use LangGraph because it matches my skills, but routing stays deterministic regardless of which framework renders the graph.

Good use of LangGraph:

- typed state
- conditional edges
- parallel identity and community nodes
- clear recovery paths

Bad use of LangGraph, avoided entirely:

- autonomous agents debating each other
- recursive delegation
- open ended tool use
- multiple large model calls for every sentence

A custom state machine is equally acceptable and is, in practice, what most of this backend actually runs on:

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

### Learn Later, Only If Needed

- Docker Compose
- request tracing
- SQLite checkpoints
- simple performance profiling

### Avoid Entirely

- Kafka
- a message broker
- mandatory Redis
- distributed microservices
- cloud only deployment
- a vector database in the critical path

None of these belong in a fully local, single laptop, hackathon timeline prototype. Every one of them adds operational complexity that does not pay for itself at this scale.

## 6. Folder Ownership

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

Every file inside this tree is mine to author, review, and keep stable. Other members write against the schemas and event types defined here, so changes here are never made silently, section 26 covers the working rule that governs this.

## 7. Task R01 — FastAPI Skeleton

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

### How I Do It

1. Create an application factory.
2. Load settings from `.env`.
3. Initialize database access in the lifespan handler.
4. Initialize model clients without blocking startup forever.
5. Register routers.
6. Add CORS only for known local development origins.
7. Add graceful shutdown that cancels workers and clears session buffers.
8. Keep a configuration switch for laptop only versus local network mode.

### Acceptance Criteria

- `/api/health` works even if the local language model is stopped
- sessions can be created, read, reset, and ended
- dashboard WebSocket connects
- mobile WebSocket connects from the same hotspot
- shutdown leaves no running audio or analysis tasks

## 8. Task R02 — Shared Event Envelope

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

- every event carries a session ID
- every final utterance has an utterance ID
- every evidence item has an evidence ID
- Python stack traces are never published to the UI
- event order per session is preserved
- malformed internal events are rejected before broadcast
- timestamps are timezone aware, consistently, everywhere

## 9. Task R03 — Call State

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

- retain the latest 60 to 120 seconds of transcript
- summarize older safe context
- never discard active critical evidence during the session
- isolate each session completely from every other session
- clear unredacted text at end of session
- support a clean reset for repeated demonstrations
- store speaker as `unknown` when the microphone mix cannot separate participants

## 10. Task R04 — Queue Based Pipeline

Recommended flow:

```text
Odil audio worker
    ↓
transcript_final queue
    ↓
Lakshay fast detector
    ↓
Rajyavardhan orchestrator
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

- Whisper never waits for the language model
- critical rules publish before deep analysis runs
- slow work runs outside the audio callback
- two overlapping deep analyses on unchanged context are avoided
- workers are cancelled cleanly when a session ends
- queue growth is capped
- finalized utterances are never silently dropped

## 11. Task R05 — Deep Analysis Triggering

Deeper analysis is invoked when:

- a critical rule fires
- fast risk exceeds 25
- two manipulation labels appear within 30 seconds
- an organization claim appears
- payment, credential, remote access, or isolation language appears
- 8 to 12 seconds pass during active speech
- at least 12 new words exist
- the user presses "Analyze now"

Configuration:

```yaml
normal_interval_seconds: 10
high_risk_interval_seconds: 4
minimum_new_words: 12
critical_immediate: true
llm_timeout_seconds: 6
structured_retry_count: 1
```

This trigger logic is the single most important piece of judgment in the whole backend. Trigger too often and the LLM becomes the bottleneck for every sentence. Trigger too rarely and genuine manipulation signals get missed until it is too late in the conversation. These specific thresholds were chosen to keep the LLM meaningfully in the loop without ever letting it gate the fast, deterministic warning path.

## 12. Task R06 — State Graph

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

Identity and community nodes run together whenever possible:

```python
identity, community = await asyncio.gather(
    verify_identity(state),
    match_community(state),
    return_exceptions=True,
)
```

An exception here is converted into an `INSUFFICIENT_DATA` result rather than crashing the session. A single failed lookup should never take down an entire live demonstration.

## 13. Task R07 — WebSocket Manager

The manager must:

- accept dashboard and mobile clients
- group connections by session
- broadcast validated events
- remove disconnected clients cleanly
- reconnect with the current snapshot
- use a local session token
- limit payload size
- prevent one slow client from blocking all other clients

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

## 14. Task R08 — Replay Controller

Replay is mandatory, not optional, for reasons covered in section 3.

Requirements:

- accept only files from `data/demo/`
- validate WAV input
- preserve natural timing
- feed Odil's same audio queue, never a separate parallel path
- support stop and reset
- publish progress as it plays
- never bypass VAD, Whisper, or detection

Request:

```json
{
  "file_name": "bank_kyc_hi_en.wav",
  "speed": 1.0
}
```

Arbitrary paths are rejected outright, this endpoint only ever reads from the fixed demo directory.

## 15. Task R09 — Local Phone Connection

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

1. Use a team hotspot if venue WiFi blocks peer devices from reaching each other.
2. Configure the firewall before the event, not during it.
3. Display a QR code for the mobile URL so pairing is instant.
4. Keep laptop only mode ready as a fallback at all times.
5. Treat caller number metadata as manual or user provided unless a reliable local source exists.

## 16. Task R10 — Health and Diagnostics

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
| LLM timeout | rules only mode continues |
| Database error | memory only mode |
| Mobile disconnected | laptop dashboard continues |
| Microphone error | offer replay |
| Malformed event | reject and log redacted error |
| Session end | cancel tasks and clear buffers |
| Frontend reconnect | send current snapshot |

Every row in that table exists because a live demonstration in front of judges cannot afford a single point of failure to take down the whole system. Each optional component degrades gracefully, the core warning path never does.

## 17. Extension — Phone Microphone Streaming

Beyond the original scope in Task R09, I built a working extension that lets the phone's own microphone become the audio source for the entire pipeline, instead of relying only on the laptop's microphone listening acoustically to a speakerphone call.

### Why this extension exists

The original design assumes the laptop microphone hears both sides of the call because the phone sits nearby on speaker. That works, but it ties the demonstration to a fixed physical arrangement, phone next to laptop, both stationary. Streaming audio from the phone itself removes that constraint entirely. The phone still has to be on speaker, no platform allows raw cellular call audio access to a browser, but now the phone can be held naturally while its own microphone captures and streams that speaker audio directly to the laptop over the local network.

### What was built

**`mobile.html`**, a single page phone client with:

- a WebSocket connection to `/ws/mobile/{session_id}`
- a risk display that changes color across four tiers, safe, caution, warning, critical
- a headline and evidence chip area driven by incoming `safety_warning` and `decision_update` events
- vibration feedback on warning and critical tiers, using the browser's native Vibration API
- a "Start Listening" control that requests microphone permission, captures audio with the Web Audio API, downsamples it from the device's native sample rate to 16kHz mono, converts it to Int16 PCM, and streams it as binary WebSocket frames roughly every 4096 samples

**`mobile_pairing.py`**, a FastAPI router with:

- `GET /mobile`, serving the static phone page
- `GET /api/v1/sessions/{session_id}/qr`, generating a QR code that encodes the pairing URL, built from an auto detected local network IP so it works identically whether the laptop and phone share ordinary WiFi or the phone's own mobile hotspot
- `WS /ws/mobile/{session_id}`, a single connection that distinguishes binary audio frames from JSON control messages on the fly, routing PCM audio into the same queue the VAD worker already reads from, and routing control messages like `call_metadata`, `heartbeat`, and `acknowledgment` into the existing state reducer

### How the loop actually works, step by step

1. A session is created, the dashboard requests a QR code from `/api/v1/sessions/{session_id}/qr`.
2. The phone scans it, opening `mobile.html` in an ordinary browser tab, no app install required.
3. The page connects its WebSocket, and the operator taps "Start Listening," granting microphone permission once.
4. The phone is placed on speaker for the call. Its own microphone now captures the acoustic audio.
5. The browser downsamples and streams that audio as binary frames over the already open WebSocket.
6. `mobile_pairing.py` receives each binary frame and pushes it into the shared audio queue, the exact same queue Odil's VAD worker was always going to read from, so nothing downstream needed to change.
7. VAD, faster-whisper, the fast detector, and the full orchestration graph run exactly as already specified in sections 10 through 12.
8. The moment a `safety_warning` or `decision_update` event is produced, the broadcaster sends it to both the dashboard and, through `push_to_mobile()`, back to the same phone that supplied the audio.
9. The phone's screen changes color, shows the reason, and vibrates, all within roughly a second or two of the words actually being spoken.

### A hard constraint this extension exposed

Browsers block microphone access on any page that is not served over HTTPS or `localhost`. Since the phone opens the laptop's local IP directly, this fails silently unless addressed. The fix used here is a locally generated self signed certificate through `mkcert`, with uvicorn started using `--ssl-keyfile` and `--ssl-certfile`, and the QR code updated to encode an `https://` URL instead of `http://`. This is a one time setup step per demonstration laptop, not something handled live, and it is the single most likely thing to silently break this feature if skipped.

### Known limitations, stated plainly

- if the phone's own speaker is too loud, its own microphone can pick up feedback from that same speaker, moderate volume avoids this
- venue WiFi with client isolation policies will block phone to laptop traffic entirely, a phone hotspot avoids this by giving full control over the network
- Safari on iOS does not support the Vibration API, the color and headline change still work everywhere, vibration is a bonus that only fires on browsers that support it

## 18. Cooperation With the Team

### With Namit

- freeze the decision schema early
- define the model timeout together
- agree on exactly what state gets sent to contextual analysis
- verify the rules only fallback behaves correctly when the LLM is unavailable

### With Odil

- agree on `AudioFrame` and `TranscriptFinal` shapes
- define cancellation behavior clearly
- keep audio processing outside the orchestration layer entirely

### With Lakshay

- expose one detector service, not several competing ones
- keep labels stable across iterations
- integrate identity lookup cleanly into the same pipeline

### With Mayank

- use repository interfaces, not direct database calls scattered everywhere
- support a memory only fallback
- avoid persistence anywhere in the time critical warning path

### With Palak

- provide mock fixtures early so the UI is never blocked waiting on the backend
- test reconnect behavior together
- test the local mobile URL together, including the phone microphone extension
- agree on friendly, non technical system error wording for the dashboard

## 19. Day by Day Work

### Day 1
- FastAPI skeleton
- event schemas
- health endpoint
- WebSocket manager

### Day 2
- replay transcript to detector to risk to dashboard

### Day 3
- CallState, queues, cooldown logic

### Day 4
- local LLM node, timeout, schema repair

### Day 5
- stabilize scam and legitimate paths

### Day 6
- microphone session and local phone page

### Day 7
- identity and community parallel nodes

### Day 8
- final machine migration

### Day 9
- latency instrumentation

### Day 10
- offline and component failure testing

### Day 11
- architecture documentation

### Day 12
- rehearsal support

### Days 13 and 14
- critical fixes, final commands, archive

## 20. Shared 14 Day Milestones

| Day | Team milestone |
|---|---|
| 1 | Repository, schemas, mock dashboard, first audio and rule tests |
| 2 | Replay audio → transcript → critical rule → risk warning → dashboard |
| 3 | VAD, expanded rules, conversation state, database |
| 4 | Structured local LLM analysis and first classifier |
| 5 | Stable replay integration with scam and legitimate scenarios |
| 6 | Live speakerphone/microphone test and local phone connection |
| 7 | Identity verification and community pattern matching |
| 8 | Full system migrated to Namit's final laptop |
| 9 | Held out evaluation and latency measurement |
| 10 | Privacy, failure, and offline testing |
| 11 | Interface polish and presentation material |
| 12 | Five full rehearsals and backup recording |
| 13 | Critical bug fixes only |
| 14 | Release freeze, archive, and final rehearsal |

## 21. Required Tests

```text
create/end session
session isolation
event validation
WebSocket broadcast
reconnect snapshot
fast warning before LLM
deep analysis cooldown
LLM timeout fallback
database failure memory mode
replay path restriction
session reset
shutdown clears workers
local mobile client reconnect
phone microphone frame ingestion
```

## 22. Final Deliverables

- FastAPI application
- typed schemas
- session state
- queues
- orchestration graph
- WebSocket manager
- replay controller
- microphone session control
- local phone connection, including phone microphone streaming
- health diagnostics
- fallback logic
- API documentation
- start and stop instructions

## 23. Judge Questions

### Why multi agent with one local model?

> Agents are specialized responsibilities and tool boundaries. Manipulation, identity, community, and decision components use different inputs and schemas but may share one local model for speed.

### Why a graph?

> A graph makes safety and latency predictable. Critical rules run first, slower contextual analysis runs conditionally, and nothing about that ordering is left to chance.

### What if a component fails?

> Rules continue without the language model, memory state continues without the database, and the laptop interface continues without the phone page.

### Why let the phone stream its own microphone instead of always using the laptop's?

> Physically it makes no difference to the pipeline, both are just PCM audio frames landing in the same queue. It does remove the constraint of keeping the phone physically next to the laptop for the whole call, and it demonstrates that the ingestion layer is genuinely source agnostic.

## 24. First 24 Hours

- create the backend
- define the event envelope
- implement health
- implement session create/end
- create the dashboard WebSocket
- accept a mock transcript
- broadcast a mock risk update
- document the commands needed to run everything

## 25. Personal Checklist

- [ ] Sessions are isolated.
- [ ] Events are typed.
- [ ] Critical warnings are not blocked.
- [ ] Timeouts exist.
- [ ] Database failure is survivable.
- [ ] WebSockets reconnect.
- [ ] Replay uses the real pipeline.
- [ ] Phone page is optional.
- [ ] Phone microphone streaming works over both WiFi and hotspot.
- [ ] HTTPS is configured so mobile microphone permission actually works.
- [ ] Shutdown clears workers.
- [ ] API is documented.

## 26. Team Wide Working Rules

1. The `main` branch must remain demoable at all times.
2. The replay based end to end pipeline must work by Day 2.
3. Every feature must expose a typed input and output.
4. Every task must include at least one test.
5. No finished module may remain only inside a notebook.
6. Interface changes require agreement from the affected members.
7. Local and private processing is the default, always.
8. Raw audio must not be committed, logged, or saved unintentionally.
9. A large language model may add context but may not remove deterministic critical warnings.
10. Optional features must never break the core demonstration.
11. Each member must maintain a short README for their module, this file is mine.
12. Every evening the team must run one scam case, one legitimate case, and one failure case.

### Shared event flow

```text
Odil: AudioFrame / TranscriptFinal
        |
        v
Lakshay: DetectionResult / IdentityLookup
        |
        v
Rajyavardhan: CallState / Agent orchestration
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

## 27. Shared Event Flow

The flow above is the backbone of the entire system, and it is worth stating explicitly why the ordering is fixed rather than flexible. Audio and transcript production must never wait on anything downstream. Detection must never wait on the language model. The language model must never be allowed to suppress a deterministic critical warning that the rule engine already raised. Persistence must never sit on the critical path where a slow disk write could delay a warning reaching the screen. The interface layer is the only consumer, it never talks back into the pipeline except through the explicit, typed control messages defined in the mobile and dashboard schemas.

## 28. Definition of Done

A task is complete only when:

- the code is committed
- another member can run it
- setup instructions exist
- input and output are documented
- a test exists
- errors are handled
- it works in the integrated branch
- it works on the final demonstration laptop when relevant
- it does not expose secrets or private data

## 29. Local Setup and Run Instructions

### Prerequisites

- Python 3.11 or newer
- `pip install -r requirements.txt`
- `pip install qrcode[pil] --break-system-packages` for the QR pairing endpoint
- `mkcert` installed, for the HTTPS certificate the phone microphone extension needs

### Generating a local certificate, once, before any demo

```bash
mkcert -install
mkcert 192.168.1.14 localhost 127.0.0.1
```

Replace `192.168.1.14` with the laptop's actual local network IP, or its hotspot assigned IP if using a phone hotspot on demo day. This produces a `.pem` key and certificate pair in the current directory.

### Running the backend

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --ssl-keyfile ./192.168.1.14-key.pem \
  --ssl-certfile ./192.168.1.14.pem
```

### Verifying health

```bash
curl -k https://127.0.0.1:8000/api/health
```

### Pairing the phone

1. Open the dashboard on the laptop, create a session.
2. Request the QR code from `GET /api/v1/sessions/{session_id}/qr`.
3. Scan it with the phone's camera, this opens `mobile.html` directly.
4. Accept the one time self signed certificate warning on the phone browser.
5. Tap "Start Listening," grant microphone permission.
6. Put the phone on speaker for the call.

### Running the replay fallback instead of a live call

```bash
curl -X POST https://127.0.0.1:8000/api/sessions/{session_id}/start-replay \
  -H "Content-Type: application/json" \
  -d '{"file_name": "bank_kyc_hi_en.wav", "speed": 1.0}' -k
```

## 30. Closing Note

This backend is, deliberately, the least visually interesting part of SurakshaCall AI, and also the part everything else depends on being correct. Odil's transcription, Lakshay's detection, Namit's risk decision, Palak's dashboard, and Mayank's persistence all only matter if the events connecting them arrive in order, on time, and without silently dropping anything when a component fails. That reliability, not any single clever feature, is what this README and everything it documents is actually in service of.
