# Lakshay — Dataset, Rule Engine, Lightweight Classifier, and Identity Verification Data

> **Project:** SurakshaCall AI  
> **Member:** Lakshay  
> **Primary role:** Fast first-stage detection and trusted identity data  
> **Secondary role:** Database-schema and risk-evaluation backup  
> **Main machine:** Intel i3 11th Gen, 16 GB RAM, 512 GB  
> **Success condition:** Dangerous requests are detected quickly while legitimate safety advice is not falsely marked critical.

---

## 1. Your Mission

You build the fast safety layer.

Your detector must react immediately to:

- OTP/PIN/CVV/password requests;
- indirect six-digit-code requests;
- payment instructions;
- screen sharing;
- remote-control applications;
- QR and collect-request scams;
- isolation and forced continuous calls;
- fake authority and threats.

It must also understand:

> “Never share your OTP.”

is safe advice.

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

1. label taxonomy;
2. normalization;
3. synthetic dialogue dataset;
4. legitimate and ambiguous cases;
5. multilingual rules;
6. safe-advice logic;
7. lightweight multilabel classifier;
8. saved model artifact;
9. training script;
10. evaluation;
11. trusted organization seed;
12. aliases;
13. number normalization;
14. published-policy contradiction data;
15. unit tests.

## 3. Technologies to Learn

### Must Learn

- JSONL;
- regular expressions;
- Hindi Unicode;
- Scikit-learn pipelines;
- sentence-transformers;
- logistic regression;
- `OneVsRestClassifier`;
- `MultiLabelBinarizer`;
- family-based dataset splitting;
- precision/recall/F1;
- joblib;
- `phonenumbers`;
- pytest;
- SQLite seed format.

### Later Only If Stable

- XLM-R fine-tuning;
- Hugging Face Trainer;
- calibration;
- active learning.

### Avoid

- training a large transformer;
- private recordings without consent;
- keyword-only detection;
- random sentence split leakage;
- claiming accuracy from seen templates;
- unnecessary vector search.

## 4. Folder Ownership

```text
backend/app/detection/
├── labels.py
├── normalizer.py
├── rules.py
├── safe_advice.py
├── classifier.py
└── service.py

backend/app/identity/
├── aliases.py
├── phone_numbers.py
├── verifier.py
└── policy_checks.py

data/dialogues/
data/trusted_directory/
data/evaluation/
models/trigger_classifier/
scripts/train_classifier.py
scripts/evaluate_detector.py
```

## 5. Task L-01 — Label Taxonomy

Utterance labels:

```text
AUTHORITY_CLAIM
URGENCY
FEAR_THREAT
ISOLATION
SECRET_REQUEST
PAYMENT_REQUEST
REMOTE_ACCESS
SCREEN_SHARE
CHANNEL_SWITCH
REWARD_SCARCITY
PERSISTENCE
SAFE_ADVICE
NORMAL_SERVICE
UNKNOWN
```

Scenario labels:

```text
BANK_KYC
DIGITAL_ARREST
UPI_REFUND
REMOTE_SUPPORT
COURIER_CUSTOMS
INVESTMENT
JOB_FEE
FAMILY_EMERGENCY
LEGITIMATE_BANK
LEGITIMATE_COURIER
AMBIGUOUS
```

Write a precise definition and positive/negative examples for every label.

## 6. Task L-02 — Dataset

Schema:

```json
{
  "dialogue_id": "bank_kyc_hi_en_001",
  "scenario": "BANK_KYC",
  "is_scam": true,
  "language": "hi-en",
  "template_family": "kyc_freeze_v1",
  "turns": [
    {
      "speaker": "caller",
      "text": "Message mein jo chhe ank aaye hain woh bataiye.",
      "labels": ["SECRET_REQUEST"]
    }
  ],
  "expected_min_risk": 85
}
```

Target:

| Category | Count |
|---|---:|
| Clear scam | 80 |
| Legitimate | 60 |
| Ambiguous | 40 |
| Safe advice with risky words | 30 |
| Total | 210 |

Day-3 minimum: 50 reviewed dialogues.

Include:

- English;
- Hindi Devanagari;
- Romanized Hindi;
- code mix;
- indirect requests;
- polite and aggressive versions;
- ASR-like spelling errors.

Review process:

1. one writer;
2. you label;
3. second reviewer checks;
4. disagreements documented;
5. assign template family.

Split by template family, not random sentence.

## 7. Task L-03 — Normalization

Maintain:

- raw text;
- normalized text;
- redacted log text.

Example:

```json
{
  "raw_text": "Sir abhi jo 6 digit ka code aya h wo btao",
  "normalized_text": "sir abhi jo six digit code aaya hai woh batao",
  "redacted_text": "sir abhi jo [SECRET_TYPE] aaya hai woh batao"
}
```

Normalize common ASR variants without destroying evidence.

## 8. Task L-04 — Deterministic Rules

Categories:

### Secret

```text
OTP
one-time password
six-digit code
verification code
message code
PIN
CVV
UPI PIN
code batao
chhe ank
ओटीपी बताइए
```

### Payment

```text
transfer now
safe account
verification account
UPI collect
approve request
scan QR
pay release fee
```

### Remote access

```text
AnyDesk
TeamViewer
QuickSupport
RustDesk
remote app
screen share
install application
```

### Isolation

```text
do not tell anyone
do not disconnect
stay on call
किसी को मत बताना
कॉल मत काटना
```

### Authority

```text
bank KYC
cybercrime
police
customs
RBI
income tax
telecom department
court
```

Output:

```json
{
  "event_id": "evt_04",
  "label": "SECRET_REQUEST",
  "confidence": 0.99,
  "severity": 5,
  "source": "rule",
  "quote": "Message mein jo code aaya hai woh bataiye.",
  "rule_id": "secret_indirect_hi_03"
}
```

## 9. Task L-05 — Safe Advice

Required behavior:

```text
"Tell me your OTP." -> SECRET_REQUEST
"Never tell anyone your OTP." -> SAFE_ADVICE
"Did you receive an OTP?" -> AMBIGUOUS
"Read the six digits." -> SECRET_REQUEST
"Bank staff never ask for a code." -> SAFE_ADVICE
```

Use:

- request verbs;
- negation;
- safety verbs;
- local sentence context;
- classifier probability;
- speaker structure where available.

## 10. Task L-06 — Lightweight Classifier

Pipeline:

```text
Text
 -> multilingual sentence embedding
 -> OneVsRest logistic regression
 -> label probabilities
```

Training:

1. flatten turns;
2. create embeddings;
3. encode labels;
4. split by family;
5. train;
6. choose thresholds;
7. save;
8. evaluate.

Save:

```text
model.joblib
label_binarizer.joblib
metadata.json
metrics.json
```

Metadata includes model name, date, counts, labels, and thresholds.

## 11. Task L-07 — Combine Rules and Classifier

Rules dominate explicit critical cases.

```python
if critical_rule:
    confidence = max(0.95, classifier_probability)
elif classifier_probability >= threshold:
    emit_classifier_event()
```

Never average a strong critical rule downward.

## 12. Task L-08 — Trusted Directory

Record:

```json
{
  "canonical_name": "Example Bank",
  "organization_type": "BANK",
  "aliases": ["example bank", "example kyc department"],
  "official_domains": ["example.org"],
  "official_numbers": ["1800000000"],
  "never_request": ["OTP", "PIN", "CVV", "password"],
  "source_url": "official source",
  "last_verified_at": "YYYY-MM-DD"
}
```

Statuses:

```text
VERIFIED_OFFICIAL_NUMBER
UNVERIFIED_NUMBER
KNOWN_REPORTED_TEST_RISK
ORGANIZATION_NOT_IN_DIRECTORY
CLAIM_CONTRADICTS_POLICY
INSUFFICIENT_DATA
```

Absence means unverified, not fraudulent.

## 13. Task L-09 — Phone Number Normalization

Use `phonenumbers`.

Normalize Indian formats. If manually entered, label the source as user-provided demo metadata.

## 14. Task L-10 — Evaluation

Report:

- per-label precision;
- recall;
- F1;
- macro F1;
- critical secret-request recall;
- safe-advice false critical rate;
- remote-access recall;
- legitimate-call false alarms.

Honest format:

```text
Held-out template families: X
Utterances: Y
Critical request recall: A/B
False critical warnings: C/D
Limitations: synthetic data, limited dialects, scripted recordings
```

## 15. Cooperation

- Odil: ASR errors and recordings.
- Namit: severity and score mapping.
- Ron: stable detector service.
- Mayank: directory seed and evaluation.
- Palak: readable labels and safe-advice demonstration.

## 16. Day-by-Day Work

### Day 1
- taxonomy;
- 25 dialogues;
- direct rules.

### Day 2
- detector service integrated.

### Day 3
- 50–75 dialogues;
- safe advice;
- normalization.

### Day 4
- first classifier.

### Day 5
- evaluation on scam/legitimate cases.

### Day 6
- live-ASR variants.

### Day 7
- directory and number normalization.

### Day 8
- final-machine test.

### Day 9
- held-out evaluation.

### Day 10
- false-positive tuning.

### Day 11
- evaluation presentation.

### Day 12
- rehearsal support.

### Days 13–14
- freeze model and critical fixes.

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
direct OTP
indirect code
Romanized Hindi
Devanagari Hindi
safe advice
ambiguous OTP
remote app
screen share
safe-account transfer
isolation
authority
unknown number not fraud
verified number
policy contradiction
model artifact load
no family leakage
```

## 18. Final Deliverables

- taxonomy;
- reviewed dialogues;
- normalization;
- rules;
- safe-advice module;
- classifier;
- training script;
- metrics;
- directory;
- phone normalization;
- policy checker;
- unit tests;
- evaluation content.

## 19. Judge Questions

### Is it only keywords?

> No. Rules protect explicit critical cases, while the lightweight multilingual classifier detects paraphrases and context. Deeper analysis is invoked only when needed.

### How do you prevent safe advice from triggering?

> Safe advice is a separate label with negation and request-structure logic, and it is a required held-out test.

### Where is the data from?

> Manually reviewed synthetic and consented test scenarios. Production requires ethically collected multilingual real-world data.

## 20. First 24 Hours

- define labels;
- write 25 dialogues;
- implement five direct and five indirect rules;
- safe-advice tests;
- detector output schema;
- give recording scripts to Odil.

## 21. Personal Checklist

- [ ] Precise labels.
- [ ] Legitimate and ambiguous data.
- [ ] Safe advice protected.
- [ ] Indirect requests detected.
- [ ] Reproducible classifier.
- [ ] No template leakage.
- [ ] Honest metrics.
- [ ] Directory sources documented.
- [ ] Unknown is not fraud.
- [ ] CPU-friendly runtime.

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
