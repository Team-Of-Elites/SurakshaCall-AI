# Odil — Local Audio Capture, Voice Activity Detection, Whisper, Replay, and Phone Connection

> **Project:** SurakshaCall AI  
> **Member:** Odil  
> **Primary role:** Local audio and speech-recognition pipeline  
> **Secondary role:** Real-time streaming and GPU-setup backup  
> **Main machine:** Lenovo Legion 5, RTX 3060, 16 GB RAM, 1 TB  
> **Success condition:** Live speakerphone or replay audio becomes timestamped transcript events quickly and reliably.

---

## 1. Your Mission

You provide the system's ears.

The live prototype uses:

1. a normal test call;
2. victim phone on speaker;
3. laptop microphone;
4. local capture;
5. Voice Activity Detection;
6. faster-whisper;
7. transcript events.

You must also build a timed replay mode for reliable demonstrations and evaluation.

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

1. `AudioFrame`;
2. microphone selection;
3. 16 kHz mono capture;
4. ring buffer;
5. VAD;
6. chunking;
7. pre/post-roll;
8. faster-whisper;
9. GPU/CPU modes;
10. final transcript events;
11. replay;
12. physical speakerphone setup;
13. audio-quality status;
14. latency measurement;
15. optional local phone metadata/session connection;
16. backup inference environment.

You do not own scam classification or risk scoring.

## 3. Technologies to Learn

### Must Learn

- PCM audio;
- sample rate;
- channels;
- int16;
- frame duration;
- `sounddevice`;
- NumPy;
- `soundfile`;
- ring buffers;
- WebRTC or Silero VAD;
- faster-whisper;
- CUDA;
- queues;
- producer/consumer design;
- microphone enumeration;
- performance timing.

Recommended:

```yaml
sample_rate: 16000
channels: 1
dtype: int16
frame_ms: 30
silence_finalize_ms: 650
pre_roll_ms: 250
post_roll_ms: 200
max_utterance_seconds: 12
ring_buffer_seconds: 20
save_raw_audio: false
```

### Later Only If Needed

- denoising;
- echo cancellation;
- speaker diarization;
- USB microphone;
- ADB port forwarding.

### Avoid

- training ASR;
- saving every chunk;
- perfect diarization;
- building a phone call recorder;
- claiming direct cellular audio access;
- deepfake work before transcription is stable.

## 4. Folder Ownership

```text
backend/app/audio/
├── interfaces.py
├── microphone.py
├── devices.py
├── ring_buffer.py
├── vad.py
├── chunker.py
├── replay.py
└── quality.py

backend/app/stt/
├── transcriber.py
├── model_loader.py
├── language.py
└── events.py

scripts/
├── list_microphones.py
├── benchmark_whisper.py
├── record_test_audio.py
└── test_audio_pipeline.py
```

## 5. Task O-01 — Common Audio Interface

```python
class AudioFrame(BaseModel):
    source: Literal["microphone", "replay"]
    track: Literal["mixed", "unknown"]
    timestamp_ms: int
    sample_rate: int
    channels: int
    pcm16: bytes
```

Rules:

- microphone and replay emit the same type;
- timestamp is monotonic;
- downstream receives 16 kHz mono PCM16;
- mixed microphone audio is not falsely labeled as separated speakers.

## 6. Task O-02 — Microphone Enumeration

Command:

```bash
python scripts/list_microphones.py
```

Support:

```env
AUDIO_DEVICE_INDEX=1
AUDIO_SAMPLE_RATE=16000
```

Requirements:

- clear missing-device error;
- fallback to system default;
- device shown in health status;
- final laptop tested early.

## 7. Task O-03 — Microphone Capture

Use a callback that quickly pushes frames to a queue.

Do not run Whisper in the callback.

Responsibilities:

- convert to consistent bytes;
- handle overflow;
- publish status;
- bridge safely to async code;
- stop cleanly.

## 8. Task O-04 — Ring Buffer

Use approximately 20 seconds.

Purpose:

- keep pre-roll;
- recover first word;
- avoid disk;
- discard old data;
- clear at end.

Test eviction and cleanup.

## 9. Task O-05 — VAD

State:

```text
SILENCE
 -> possible speech
 -> SPEECH
 -> silence for 650 ms
 -> finalize
 -> SILENCE
```

Test:

- short words;
- long monologue;
- notifications;
- fan noise;
- overlapping speech;
- phone-speaker distortion.

Acceptance:

- silence not repeatedly transcribed;
- first/last words retained;
- maximum utterance enforced;
- acceptable latency.

## 10. Task O-06 — Timed Replay

Requirements:

- allowed demo directory;
- validate WAV;
- convert to 16 kHz mono;
- emit 20–30 ms frames;
- natural speed;
- stop/reset;
- publish progress;
- use the exact live pipeline.

## 11. Task O-07 — faster-whisper

Start:

```yaml
model: small
device: cuda
compute_type: float16
```

Fallback:

```yaml
model: base_or_small
device: cpu
compute_type: int8
```

Load once.

Transcript:

```json
{
  "utterance_id": "utt_17",
  "session_id": "call_001",
  "track": "mixed",
  "speaker": "unknown",
  "text": "Your account will be blocked in ten minutes.",
  "language": "en",
  "started_ms": 41000,
  "ended_ms": 44700,
  "asr_confidence": 0.82,
  "input_mode": "microphone"
}
```

Never invent speaker identity.

## 12. Task O-08 — Hindi/Code-Mixed Testing

Test:

```text
Main bank ke KYC department se bol raha hoon.
Aapka account das minute mein block ho jayega.
Message mein jo six-digit code aaya hai woh bataiye.
Kisi ko mat batana.
UPI PIN enter kijiye.
```

Safe:

```text
Kisi ko bhi OTP ya PIN mat batana.
Official app se verify kijiye.
```

Maintain an ASR error log and give recurring errors to Lakshay.

## 13. Task O-09 — Audio Quality

States:

```text
GOOD
LOW_VOLUME
CLIPPING
NOISY
NO_INPUT
DEVICE_ERROR
```

Use RMS, clipping percentage, silence duration, dropped frames.

Provide actionable text:

> Move the phone closer to the laptop microphone.

## 14. Task O-10 — Physical Setup

```text
Caller phone
    ↓ normal call
Victim phone on speaker
    ↓ 20–40 cm
Laptop microphone
```

Test volume, gain, distance, echo, vibration, fan noise, orientation.

Mark ideal position during rehearsal.

## 15. Task O-11 — Optional Local Phone Connector

The phone may:

- open mobile warning;
- start/end session;
- send manually entered number;
- receive risk;
- show privacy.

Use same hotspot or optional USB port forwarding.

Do not promise call-audio extraction.

## 16. Task O-12 — Latency

Record:

```text
speech end
utterance finalize
Whisper start
Whisper finish
fast warning
full decision
```

Report median and maximum.

Target critical phrase to fast warning: under 3 seconds, only after measurement.

## 17. Failure Handling

| Failure | Action |
|---|---|
| Microphone missing | offer replay |
| CUDA error | CPU int8 |
| Model missing | setup message |
| No speech | low-volume/no-input |
| Long speech | split |
| Overlap | speaker unknown |
| Invalid replay | reject |
| Session end | stop and clear |

## 18. Cooperation

- Lakshay: ASR variants and recording scripts.
- Ron: queues and cancellation.
- Namit: model benchmark and latency.
- Palak: audio status.
- Mayank: no persistence and metrics.

## 19. Day-by-Day Work

### Day 1
- install;
- list microphone;
- file transcription;
- `AudioFrame`.

### Day 2
- timed replay and transcript event.

### Day 3
- microphone, ring buffer, VAD.

### Day 4
- RTX benchmark.

### Day 5
- stable replay scenarios.

### Day 6
- live speakerphone test.

### Day 7
- Hindi/code mix and phone page support.

### Day 8
- final laptop.

### Day 9
- latency and critical misses.

### Day 10
- CPU/noise/device fallback.

### Day 11
- technical explanation.

### Day 12
- physical setup rehearsal.

### Days 13–14
- critical fixes and cache backup.

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
audio schema
device enumeration
missing device
ring eviction
VAD start
VAD finalize
max split
replay timing
replay reset
model loads once
Hindi transcription
safe-advice transcription
session cleanup
CPU fallback
quality states
```

## 21. Final Deliverables

- audio interface;
- microphone;
- device selector;
- ring buffer;
- VAD;
- chunker;
- replay;
- Whisper wrapper;
- transcript events;
- quality monitor;
- benchmark;
- latency report;
- physical setup guide;
- fallback configuration.

## 22. Judge Questions

### How do you access audio?

> The test phone is on speaker and the local laptop microphone captures the conversation. A consented recording can also be replayed through the same pipeline. We do not claim unrestricted cellular-call capture.

### Why local Whisper?

> It reduces privacy exposure and supports offline safety analysis.

### What about overlapping speakers?

> The microphone mix may not support reliable separation, so speaker is marked unknown while dangerous requests are still detected.

## 23. First 24 Hours

- install Whisper;
- list microphones;
- transcribe English/Hindi;
- implement replay;
- define transcript event;
- share ASR examples;
- benchmark RTX 3060.

## 24. Personal Checklist

- [ ] Microphone works.
- [ ] Replay works.
- [ ] Same interface.
- [ ] VAD handles silence.
- [ ] Model loads once.
- [ ] Hindi tested.
- [ ] No invented speaker.
- [ ] Raw audio not saved.
- [ ] Buffers clear.
- [ ] CPU fallback.
- [ ] Latency measured.
- [ ] Final laptop tested.

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
