<h1 align="center">🛡️ SurakshaCall AI</h1>
<h3 align="center">Privacy-First Real-Time Scam Call Behavioral Analyzer</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/FastAPI-0.111-green?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/Whisper-faster--whisper-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LLM-Ollama%20Local-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Privacy-100%25%20Local-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/SIH-2026-gold?style=for-the-badge" />
</p>

<p align="center">
  <b>Submitted for Smart India Hackathon 2026</b><br/>
  A multi-stage AI pipeline that detects psychological manipulation and dangerous requests during suspicious phone calls — in real time, entirely on-device, with zero cloud uploads.
</p>

---

## 📌 The Problem

Existing spam-call solutions (Truecaller, blocklists, TRAI Chakshu) depend on **previously reported numbers**. Scammers evade them by:

- Using freshly purchased SIMs or spoofed numbers
- Speaking politely before slowly escalating pressure
- Avoiding obvious scam keywords
- Using Hindi, English, or Hinglish code-mixed speech
- Asking to install remote-access apps instead of directly demanding money

> **A brand-new number with a classic scam script is invisible to every existing tool. It is not invisible to us.**

---

## 💡 Our Solution

**SurakshaCall AI** analyzes the **behavior of the conversation itself**, not the caller's number. It detects:

| Manipulation Tactic | Example |
|:---|:---|
| 🎭 **Authority Fabrication** | "Main CBI Inspector Sharma bol raha hoon" |
| ⏰ **Urgency Engineering** | "10 minute mein transfer karo warna arrest" |
| 😰 **Fear Induction** | "Non-bailable warrant issue hua hai" |
| 🔇 **Isolation Enforcement** | "Kisi ko mat batana, yeh classified case hai" |
| 🔑 **Secret Requests** | "Jo 6 digit code aaya hai woh bataiye" |
| 💻 **Remote Access** | "AnyDesk install karo abhi" |
| 💸 **Payment Extraction** | "Safe account mein transfer karo" |

### Output — Explainable Risk Index

```
Risk Index: 92 / 100 — CRITICAL

Immediate Action: Do NOT share the code. End the call.

Evidence Detected:
  • Caller claimed CBI authority           (AUTHORITY_CLAIM)
  • Threatened arrest within 10 minutes    (URGENCY + FEAR_THREAT)
  • Requested 6-digit OTP                  (SECRET_REQUEST — severity 5)
  • Instructed victim not to inform family (ISOLATION)

Identity Check:
  • Calling number: Unverified VoIP — not a government landline
  • Claimed identity: CBI — not found in trusted directory
  • Policy contradiction: CBI never requests money over a phone call

Scam Type: DIGITAL_ARREST — Stage 3 / 5
Recommended: Hang up. Call 1930 (Cyber Crime Helpline).
```

---

## 🏗️ System Architecture

```
📱 Phone Call on Speaker
        │
        ▼
🎙️ Laptop Microphone (acoustic capture)
        │
        ▼
🔉 Voice Activity Detection (Silero VAD / WebRTC VAD)
        │
        ▼
📝 faster-whisper STT ──► Transcript Normalizer
        │                        │
        ▼                        ▼
⚡ Fast Rule Engine +      Conversation State
   Lightweight Classifier  (rolling window)
        │
        ├── No critical event ──► Continue monitoring
        │
        └── Critical detected ──► Multi-Agent Analysis
                                        │
                          ┌─────────────┼─────────────┐
                          ▼             ▼             ▼
                  🔍 Identity    🧠 LLM Context  👥 Community
                  Verifier       Analyzer        Pattern Match
                          │             │             │
                          └─────────────┴─────────────┘
                                        │
                                        ▼
                              ⚖️ Risk Decision Engine
                                        │
                          ┌─────────────┼─────────────┐
                          ▼             ▼             ▼
                   📊 Dashboard   📱 Phone UI   📋 Evidence Log
```

### Two-Stage Detection Design

| Stage | Component | Speed | Purpose |
|:---|:---|:---|:---|
| **Stage 1** | Deterministic rules + Lightweight classifier | < 50 ms | Catch every critical request immediately |
| **Stage 2** | Local LLM (Ollama) | 3–8 sec | Deep context, reasoning, explainable output |

The LLM is invoked **only when needed** — keeping the system fast and resource-efficient.

---

## 🔒 Privacy Architecture

```
ON-DEVICE — Nothing Leaves the Laptop
┌─────────────────────────────────────────────┐
│  Audio ──► VAD ──► faster-whisper           │
│                         │                   │
│              Transcript (in-memory only)    │
│                         │                   │
│              Ollama LLM (local server)      │
│                         │                   │
│              Risk Analysis + Dashboard      │
│                                             │
│  🗑️ Audio buffer: cleared after processing │
│  🗑️ Transcript: cleared after session end  │
└─────────────────────────────────────────────┘

OPTIONALLY SHARED — Anonymous Pattern Only
┌─────────────────────────────────────────────┐
│  { "tactics": ["URGENCY","FEAR_THREAT"],    │
│    "scam_type": "DIGITAL_ARREST",           │
│    "number_hash": "sha256:a3f2...",         │
│    "risk_score": 92 }                       │
│  NO transcript. NO audio. NO PII.           │
└─────────────────────────────────────────────┘
```

> ⚠️ **Prototype Notice:** Audio is captured by the local laptop microphone while the phone is on speakerphone, or from consented pre-recorded test audio. All analysis runs locally. This system does not intercept cellular calls.

---

## 🛠️ Technology Stack

| Layer | Technology | Cost |
|:---|:---|:---|
| Language | Python 3.11+ | Free |
| Backend | FastAPI + Uvicorn | Free |
| Real-time | WebSocket (native FastAPI) | Free |
| Audio Capture | sounddevice + numpy | Free |
| VAD | Silero VAD (via faster-whisper) | Free |
| Speech-to-Text | faster-whisper small, INT8 | Free |
| Hindi ASR | IndicWhisper weights (AI4Bharat) | Free |
| LLM | Ollama + qwen3:4b / llama3.2 / gemma2:2b | Free |
| Rule Engine | Python regex + custom patterns | Free |
| Classifier | sentence-transformers + scikit-learn | Free |
| Database | SQLite3 (built-in Python) | Free |
| Number Analysis | phonenumbers library | Free |
| Frontend | Vanilla HTML + CSS + JavaScript | Free |
| Testing | pytest | Free |
| **Total Cost** | **₹0 — 100% local, 100% offline** | **Free** |

---

## 📁 Repository Structure

```
SurakshaCall-AI/
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entry point + WebSocket
│   │   ├── session.py                  # Call session state management
│   │   │
│   │   ├── detection/                  # ── Lakshay ──
│   │   │   ├── labels.py               # 14 utterance + 11 scenario labels
│   │   │   ├── normalizer.py           # Raw → normalized → redacted text
│   │   │   ├── rules.py                # Deterministic critical-event rules
│   │   │   ├── safe_advice.py          # Safe-advice false-positive guard
│   │   │   ├── classifier.py           # Embedding + logistic regression
│   │   │   └── service.py              # Detection API contract
│   │   │
│   │   ├── identity/                   # ── Lakshay ──
│   │   │   ├── aliases.py              # Organization name aliases
│   │   │   ├── phone_numbers.py        # Number normalization
│   │   │   ├── verifier.py             # Trusted-directory + claim mismatch
│   │   │   └── policy_checks.py        # "CBI never asks for money" rules
│   │   │
│   │   ├── audio/                      # ── Odil ──
│   │   │   ├── capture.py              # sounddevice microphone capture
│   │   │   ├── vad.py                  # Voice Activity Detection
│   │   │   ├── whisper_runner.py       # faster-whisper STT pipeline
│   │   │   └── replay.py              # Timed WAV replay for demo
│   │   │
│   │   ├── agents/                     # ── Ron ──
│   │   │   ├── orchestrator.py         # Multi-agent coordination
│   │   │   ├── context_agent.py        # LLM contextual analysis
│   │   │   ├── identity_agent.py       # Identity verification calls
│   │   │   └── community_agent.py      # Community pattern lookup
│   │   │
│   │   ├── risk/                       # ── Namit ──
│   │   │   ├── scorer.py               # Risk Index aggregation (0–100)
│   │   │   ├── explainer.py            # Evidence timeline builder
│   │   │   └── decision.py             # Final RiskDecision output
│   │   │
│   │   └── db/                         # ── Mayank ──
│   │       ├── models.py               # SQLite schema
│   │       ├── session_store.py        # Session + evidence persistence
│   │       ├── community.py            # Anonymous pattern matching
│   │       └── privacy.py             # Data-clearing + audit functions
│   │
│   └── routers/
│       ├── session.py                  # POST /session/start, /session/end
│       ├── audio.py                    # WS /ws/audio
│       ├── mobile.py                   # WS /ws/mobile (phone companion)
│       └── detection.py               # GET /detection/history
│
├── frontend/                           # ── Palak ──
│   ├── README.md                       # Frontend run guide
│   ├── index.html                      # Main dashboard
│   ├── mobile.html                     # Phone companion warning page
│   ├── css/app.css                     # Dashboard styling
│   └── js/
│       └── app.js                      # REST + WebSocket dashboard client
│
├── data/
│   ├── dialogues/                      # JSONL dataset (Lakshay)
│   ├── trusted_directory/              # Verified org seed data (Lakshay)
│   └── evaluation/                     # Held-out test results
│
├── models/trigger_classifier/
│   ├── model.joblib
│   ├── label_binarizer.joblib
│   ├── metadata.json
│   └── metrics.json
│
├── scripts/
│   ├── train_classifier.py
│   └── evaluate_detector.py
│
├── tests/
│   ├── test_rules.py
│   ├── test_classifier.py
│   ├── test_identity.py
│   ├── test_risk_scorer.py
│   └── test_integration.py
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com/download) installed and running
- ffmpeg installed
- A laptop microphone
- A modern browser

### 1. Clone & Install

```bash
git clone https://github.com/Rajyavardhan11/AI-Scam-call-Psychology-Analyzer.git
cd AI-Scam-call-Psychology-Analyzer
pip install -r requirements.txt
```

### 2. Pull the Local LLM

```bash
# Choose based on your RAM:
ollama pull qwen3:4b      # Best reasoning  — ~6GB RAM
ollama pull llama3.2      # Fast fallback    — ~6GB RAM
ollama pull gemma2:2b     # Lightest option  — ~4GB RAM
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env to set your preferred model
```

### 4. Run the Backend

```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

The frontend defaults to `http://127.0.0.1:8000` as the backend API URL.

### 5. Run the Frontend Dashboard

Open a second terminal:

```bash
cd frontend
python -m http.server 5173 --bind 127.0.0.1
```

Then open:

```
http://127.0.0.1:5173/
```

In the dashboard:

1. Keep `Backend Base URL` as `http://127.0.0.1:8000`.
2. Click `Check Health`.
3. Click `Create`.
4. Click `Connect WS` if the WebSocket is not already connected.
5. Use `OTP Sample` + `Submit Transcript` to test a critical-risk detection.

### 6. Connect Your Phone (Optional)

Create a session in the dashboard first, then click `Load Pairing`. Open the generated phone URL on the mobile device.

**Via USB (ADB — most reliable):**
```bash
adb devices
adb reverse tcp:8000 tcp:8000
# Then open the dashboard pairing URL for the current session.
```

**Via Local Wi-Fi:**
```
http://<your-laptop-ip>:8000/mobile/<session-id>
```

For Wi-Fi demos, bind the backend to the LAN interface and allow the frontend origin:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

If the frontend is not served from `http://127.0.0.1:5173`, set `CORS_ORIGINS` in `.env` to include the frontend URL.

---

## 🎯 Detection Labels

### Utterance Labels

| Label | Severity | Description |
|:---|:---|:---|
| `SECRET_REQUEST` | 🔴 Critical (5) | OTP, PIN, CVV, 6-digit code requests |
| `REMOTE_ACCESS` | 🔴 Critical (5) | AnyDesk, TeamViewer, QuickSupport install |
| `PAYMENT_REQUEST` | 🔴 Critical (5) | Safe account transfer, UPI collect, QR scan |
| `ISOLATION` | 🔴 High (4) | "Don't tell anyone", "Stay on call" |
| `FEAR_THREAT` | 🟠 High (4) | Arrest threats, account freeze, legal action |
| `AUTHORITY_CLAIM` | 🟠 Medium (3) | CBI, RBI, SBI, Police impersonation |
| `URGENCY` | 🟠 Medium (3) | Time-bound pressure, "10 minutes", "right now" |
| `SCREEN_SHARE` | 🟠 Medium (3) | Screen sharing requests |
| `CHANNEL_SWITCH` | 🟡 Low (2) | Move to WhatsApp, Telegram, video call |
| `REWARD_SCARCITY` | 🟡 Low (2) | "You've won", "last chance" |
| `PERSISTENCE` | 🟡 Low (2) | "Don't disconnect", call maintenance pressure |
| `SAFE_ADVICE` | ✅ Safe | "Never share your OTP" — protective guidance |
| `NORMAL_SERVICE` | ✅ Normal | Routine, legitimate call content |
| `UNKNOWN` | ⚪ None | Insufficient context to classify |

### Scenario Labels

`BANK_KYC` · `DIGITAL_ARREST` · `UPI_REFUND` · `REMOTE_SUPPORT` · `COURIER_CUSTOMS` · `INVESTMENT` · `JOB_FEE` · `FAMILY_EMERGENCY` · `LEGITIMATE_BANK` · `LEGITIMATE_COURIER` · `AMBIGUOUS`

---

## 👥 Team

| Member | Role | Owns |
|:---|:---|:---|
| **Namit** (Lead) | AI Decision Engine, Risk Scoring, Integration | `backend/app/risk/` |
| **Lakshay** | Dataset, Rules, Classifier, Identity Verification | `backend/app/detection/` + `identity/` |
| **Ron** | Multi-Agent Orchestration, FastAPI, WebSockets | `backend/app/agents/` + `routers/` |
| **Palak** | Frontend Dashboard, UI/UX, Mobile Companion | `frontend/` |
| **Odil** | Audio Capture, VAD, Whisper, Replay Mode | `backend/app/audio/` |
| **Mayank** | Database, Community Intelligence, Privacy, QA | `backend/app/db/` + `tests/` |

---

## 📊 14-Day Build Roadmap

| Day | Milestone |
|:---|:---|
| 1 | Repository, schemas, mock dashboard, first audio and rule tests |
| 2 | Replay audio → transcript → critical rule → risk warning → dashboard |
| 3 | VAD, expanded rules, conversation state, database |
| 4 | Structured local LLM analysis and first classifier |
| 5 | Stable replay integration with scam and legitimate scenarios |
| 6 | Live speakerphone/microphone test and phone connection |
| 7 | Identity verification and community-pattern matching |
| 8 | Full system migrated to final demo laptop |
| 9 | Held-out evaluation and latency measurement |
| 10 | Privacy, failure, and offline testing |
| 11 | Interface polish and presentation material |
| 12 | Five full rehearsals and backup recording |
| 13 | Critical bug fixes only |
| 14 | Release freeze, archive, and final rehearsal |

---

## 🧪 Demo Scenarios

| Scenario | Language | Expected Risk |
|:---|:---|:---|
| Digital Arrest — CBI Impersonation | Hinglish | 90+ / Critical |
| Bank KYC Freeze — OTP Request | Hindi | 88+ / Critical |
| UPI Refund — Collect Request Scam | English | 85+ / High |
| Remote Support — AnyDesk Install | English | 92+ / Critical |
| Legitimate SBI Fraud Alert Call | English | < 20 / Safe |
| Legitimate TRAI Notice | Hindi | < 25 / Safe |

---

## 📈 Competitive Positioning

| Feature | Truecaller | Airtel Shield | Sanchar Saathi | **SurakshaCall AI** |
|:---|:---|:---|:---|:---|
| Spam number detection | ✅ | ✅ | ❌ | ✅ |
| Works on unknown new numbers | ❌ | ❌ | ❌ | **✅** |
| Psychological tactic detection | ❌ | ❌ | ❌ | **✅** |
| Scam stage identification | ❌ | ❌ | ❌ | **✅** |
| Explainable evidence per claim | ❌ | ❌ | ❌ | **✅** |
| Real-time coaching during call | ❌ | ❌ | ❌ | **✅** |
| 100% local — no cloud upload | ❌ | ❌ | N/A | **✅** |
| Works offline | ❌ | ❌ | ❌ | **✅** |

---

## 📋 requirements.txt

```
faster-whisper>=1.0.3
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
websockets>=12.0
python-multipart>=0.0.9
sounddevice>=0.4.6
numpy>=1.26.0
soundfile>=0.12.1
ffmpeg-python>=0.2.0
phonenumbers>=8.13.37
sentence-transformers>=3.0.0
scikit-learn>=1.4.0
joblib>=1.4.0
ollama>=0.2.1
pytest>=8.2.2
```

---

## ⚙️ .env.example

```env
LLM_MODEL=qwen3:4b
AUDIO_SAMPLE_RATE=16000
ANALYSIS_CHUNK_SECONDS=2.0
MAX_AUDIO_BUFFER_SECONDS=20
SAVE_RAW_AUDIO=false
WHISPER_MODEL=small
WHISPER_COMPUTE_TYPE=int8
WHISPER_DEVICE=cpu
RISK_THRESHOLD_MEDIUM=40
RISK_THRESHOLD_HIGH=70
RISK_THRESHOLD_CRITICAL=85
CLEAR_SESSION_ON_END=true
LOG_REDACTED_ONLY=true
```

---

## 🔒 Privacy Commitments

- ✅ Audio processed in-memory only — never written to disk by default
- ✅ Speech recognition runs locally via faster-whisper
- ✅ AI analysis runs locally via Ollama — no cloud API calls
- ✅ Logs contain redacted text only — sensitive values replaced with `[SECRET_TYPE]`
- ✅ Phone numbers stored as SHA-256 hashes only
- ✅ Session data cleared on call end
- ✅ Community sharing uses anonymous pattern fingerprints — no transcript text, no PII

---

## 📜 Ethical & Legal Disclaimer

This prototype is built for demonstration at Smart India Hackathon 2026. All test audio used in this project consists of consented scenarios created by the team. This system:

- Does **not** intercept live cellular call audio without device owner knowledge
- Does **not** build databases of personal phone numbers
- Does **not** make definitive criminal determinations about any caller
- Does **not** automatically block, report, or take action without user decision

---

## 🆘 Emergency Helplines

| Service | Contact |
|:---|:---|
| **Cyber Crime Helpline** | **1930** |
| National Cyber Crime Portal | cybercrime.gov.in |
| Report Fraud Communication | sancharsaathi.gov.in |

---

<p align="center">
  Built with ❤️ for Smart India Hackathon 2026<br/>
  <b>SurakshaCall AI — Detect the manipulation. Not just the number.</b>
</p>
