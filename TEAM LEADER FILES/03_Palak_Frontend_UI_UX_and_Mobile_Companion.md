# Palak — Frontend Dashboard, UI/UX, Mobile Companion, and Presentation Experience

> **Project:** SurakshaCall AI  
> **Member:** Palak  
> **Primary role:** User-facing product experience  
> **Secondary role:** Frontend integration and presentation  
> **Main machine:** Intel i7 13th Gen, 16 GB RAM, 512 GB  
> **Success condition:** A judge or user understands the danger, evidence, and next safe action within two seconds.

---

## 1. Your Mission

The AI is useful only when the user understands what to do.

Your interface must show:

- current risk;
- immediate action;
- exact evidence;
- claimed identity;
- verification status;
- privacy state;
- connection state;
- live transcript;
- optional phone warning.

The system must look like one safety product, not a set of terminal windows.

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

1. desktop dashboard;
2. responsive mobile warning page;
3. component structure;
4. WebSocket event consumption;
5. reconnect and session reset;
6. live transcript;
7. risk visualization;
8. immediate-action card;
9. evidence timeline;
10. identity card;
11. community-pattern card;
12. privacy panel;
13. English/Hindi interface;
14. connection health;
15. demo controls;
16. local production build;
17. screenshots and presentation graphics.

A native Android app is optional and should not begin until the mobile web page is stable.

## 3. Technologies to Learn

### Must Learn

- React;
- TypeScript;
- Vite or Next.js;
- browser WebSocket;
- typed reducers;
- responsive CSS;
- Tailwind or CSS modules;
- accessibility;
- production builds;
- local network URLs;
- error boundaries.

Recommended:

```text
React + TypeScript + Vite
```

### Later Only If Needed

- Recharts;
- PWA installation;
- browser notifications;
- QR-code generation;
- simple sound/vibration alerts;
- Android WebView wrapper.

### Avoid

- several UI frameworks;
- Redux without need;
- Firebase as a core dependency;
- complicated animation;
- native overlays;
- saving transcript in local storage;
- making phone UI mandatory.

## 4. Folder Ownership

```text
frontend/src/
├── App.tsx
├── pages/
│   ├── Dashboard.tsx
│   └── MobileWarning.tsx
├── components/
│   ├── RiskHero.tsx
│   ├── ImmediateAction.tsx
│   ├── TranscriptPanel.tsx
│   ├── EvidenceTimeline.tsx
│   ├── IdentityCard.tsx
│   ├── CommunityCard.tsx
│   ├── PrivacyPanel.tsx
│   ├── ConnectionStatus.tsx
│   └── ModeSelector.tsx
├── hooks/
│   ├── useSessionSocket.ts
│   └── useSessionState.ts
├── types/events.ts
├── i18n/
│   ├── en.ts
│   └── hi.ts
└── styles/
```

## 5. Task P-01 — Static Dashboard Before Backend

Use mock JSON matching the final event schema.

Required layout:

```text
┌─────────────────────────────────────────────────────────────┐
│ SurakshaCall AI   LIVE   Local Processing   Audio Not Saved │
├───────────────────────┬─────────────────────────────────────┤
│ Risk Index 92/100     │ IMMEDIATE ACTION                    │
│ CRITICAL              │ DO NOT SHARE THE CODE               │
│ [progress/gauge]      │ End call and verify independently   │
├───────────────────────┼─────────────────────────────────────┤
│ Caller Claim          │ Verification                        │
│ Bank KYC Department   │ Number not verified                 │
├─────────────────────────────────────────────────────────────┤
│ Why this is suspicious                                     │
├─────────────────────────────────────────────────────────────┤
│ Live transcript                                             │
├─────────────────────────────────────────────────────────────┤
│ Privacy | Connection | System status                        │
└─────────────────────────────────────────────────────────────┘
```

Acceptance:

- critical action visible without scrolling;
- 1366×768 works;
- mobile width works;
- legitimate state looks calm;
- risk is not communicated only by color.

## 6. Task P-02 — Typed Events

```typescript
export type EventEnvelope<T = Record<string, unknown>> = {
  type: string;
  session_id: string;
  timestamp: string;
  payload: T;
};
```

Create payload types for transcript, evidence, risk, identity, community, privacy, and status.

Avoid `any`.

## 7. Task P-03 — WebSocket Hook

`useSessionSocket` must:

1. connect;
2. show status;
3. parse safely;
4. reconnect with backoff;
5. ignore malformed events;
6. accept current session snapshot;
7. close on unmount;
8. prevent duplicate listeners.

States:

```text
Connecting
Connected
Reconnecting
Offline
Session ended
```

## 8. Task P-04 — Risk Hero

Show:

```text
92/100
CRITICAL
Do not share the code.
```

Risk text:

| Level | Guidance |
|---|---|
| LOW | No strong scam behavior detected yet |
| CAUTION | Verify the caller before acting |
| HIGH | Do not take financial action during this call |
| CRITICAL | Stop. Do not share secrets or transfer money |

Accessibility:

- text labels;
- strong contrast;
- no flashing;
- keyboard support;
- careful `aria-live`.

## 9. Task P-05 — Immediate Action

At most three actions:

```text
DO NOT SHARE THE OTP

1. Do not read the code.
2. End the call.
3. Verify through the official application.
```

This card is more important than the gauge.

## 10. Task P-06 — Transcript Panel

Each utterance shows:

- timestamp;
- speaker only when known;
- text;
- evidence highlight;
- auto-scroll;
- pause auto-scroll when user reads older lines.

In microphone mode, `unknown` is acceptable. Never invent caller/user.

## 11. Task P-07 — Evidence Timeline

Item:

```text
00:24  SECRET REQUEST  Severity 5
“Tell me the six-digit code.”
The caller requested confidential authentication information.
```

Requirements:

- chronological;
- click to transcript;
- newest critical evidence visible;
- technical source hidden in normal mode;
- no unsupported model evidence.

## 12. Task P-08 — Identity Card

Verified:

```text
Claimed organization: Example Bank
Directory status: Verified demo number
```

Unverified:

```text
Number not found in the limited directory.
This does not prove fraud. Verify independently.
```

Insufficient:

```text
No reliable identity information available.
```

Never show “definitely fake” from absence alone.

## 13. Task P-09 — Community Pattern Card

```text
Similar prototype pattern found

KYC account-freeze pattern
Shared traits:
• bank authority
• urgent threat
• secret-code request
```

State that patterns are anonymous and synthetic for the prototype.

## 14. Task P-10 — Privacy Panel

Microphone mode:

```text
Audio source: Laptop microphone
Raw audio saved: No
AI processing: Local laptop
Transcript retention: Current session
Community sharing: Off
```

Replay mode:

```text
Audio source: Consented demonstration recording
AI processing: Local laptop
Session transcript: Cleared after reset
```

## 15. Task P-11 — Mobile Warning Page

Route:

```text
/mobile/{sessionId}
```

Show only:

- connection;
- risk;
- headline;
- three actions;
- caller claim;
- session status.

Provide QR code for:

```text
http://LAPTOP_LOCAL_IP:5173/mobile/{sessionId}
```

Test with a team hotspot. Keep laptop-only fallback.

## 16. Task P-12 — English and Hindi

Use reviewed translation objects.

```typescript
const en = {
  critical: "Critical",
  doNotShareCode: "Do not share the code",
};

const hi = {
  critical: "गंभीर खतरा",
  doNotShareCode: "कोड साझा न करें",
};
```

Keep warnings short and natural.

## 17. Task P-13 — Demo Controls

Desktop technical panel:

- create session;
- choose microphone/replay;
- choose replay scenario;
- start;
- stop;
- reset;
- health;
- open mobile view.

Hide these controls from the mobile user.

## 18. Task P-14 — Presentation Assets

Create:

- local architecture graphic;
- multi-agent flow;
- privacy flow;
- risk progression screenshot;
- scam versus legitimate comparison;
- team role diagram;
- technology stack graphic.

Use actual screenshots where possible.

## 19. Cooperation

### Ron
- event schema;
- reconnect;
- snapshot;
- local phone URL.

### Namit
- warning wording;
- risk levels;
- uncertainty.

### Mayank
- redaction;
- community/identity data;
- reset.

### Odil
- audio-quality status;
- microphone instructions.

### Lakshay
- label descriptions;
- safe-advice contrast.

## 20. Day-by-Day Work

### Day 1
- project setup;
- static dashboard;
- critical and legitimate mock states.

### Day 2
- WebSocket and live risk.

### Day 3
- transcript and evidence timeline.

### Day 4
- explanations and system status.

### Day 5
- stable replay interface.

### Day 6
- mobile page and local network test.

### Day 7
- identity/community cards.

### Day 8
- final-machine and phone test.

### Day 9
- fix confusion found during evaluation.

### Day 10
- privacy, reconnect, offline states.

### Day 11
- polish and presentation graphics.

### Day 12
- rehearsals and backup recording.

### Days 13–14
- critical UI fixes and production build.

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

## 21. Required Tests

```text
all risk levels render
critical action above fold
transcript append
evidence link
duplicate event ignored
malformed event handled
reconnect
snapshot restore
language toggle
privacy text
mobile responsive
reset clears transcript
```

## 22. Final Deliverables

- desktop dashboard;
- mobile warning page;
- typed events;
- socket hook;
- risk hero;
- action card;
- transcript;
- evidence;
- identity/community cards;
- privacy panel;
- bilingual copy;
- demo controls;
- production build;
- presentation visuals.

## 23. Judge Questions

### Why show evidence?

> A warning without evidence is easy to ignore. We show the exact behavior and sentence, followed by one clear safe action.

### How is it accessible?

> Large text, simple wording, limited actions, and no dependence on color alone.

### Why not end the call automatically?

> The system keeps the user in control and avoids a high-impact automatic action based on uncertain analysis.

## 24. First 24 Hours

- create React TypeScript app;
- build dashboard;
- create mock events;
- render critical and legitimate states;
- agree on events with Ron;
- test laptop and mobile widths.

## 25. Personal Checklist

- [ ] Action appears first.
- [ ] Risk is not color-only.
- [ ] Evidence links to transcript.
- [ ] Unverified is explained honestly.
- [ ] Privacy text is accurate.
- [ ] WebSocket reconnects.
- [ ] Mobile works locally.
- [ ] Reset clears private content.
- [ ] Production build runs offline.

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
