# Commit Documentation: Lakshay's Detection, Classifier & Identity Module

## 1. Commit Summary
* **Commit Title:** Integrate Lakshay's Detection Rules, ML Classifier, and Identity Verification Engines (L-01 to L-10)
* **Date & Time:** 2026-07-27 01:15 IST
* **Objective:** Implement Lakshay's entire assigned module (fast deterministic safety rules, ML classifier, identity/phone normalization, trusted seed directory, and safe advice filters) within the SurakshaCall AI repository structure.
* **Why this change was made:** To provide the fast first-stage safety layer of SurakshaCall AI that reacts immediately to dangerous requests (OTP, PIN, payment, remote access, arrest threats) while preventing false positives on legitimate advice or calls.

---

## 2. Files Modified

### Added Files:
* `backend/app/detection/labels.py` — Label taxonomy (14 utterance labels, 11 scenario labels, severity map).
* `backend/app/detection/rules.py` — Deterministic English rule engine (30+ regex rules).
* `backend/app/detection/normalizer.py` — Text normalization & PII redaction (OTP, phone, PAN, Aadhaar, email).
* `backend/app/detection/safe_advice.py` — 3-layer safe advice guard filter preventing false alarms.
* `backend/app/detection/classifier.py` — Scikit-learn + SentenceTransformers inference wrapper.
* `backend/app/identity/__init__.py` — Package init.
* `backend/app/identity/phone_numbers.py` — Phonenumbers library integration with TRAI 160-series detection.
* `backend/app/identity/aliases.py` — Canonical organization alias mapper.
* `backend/app/identity/policy_checks.py` — Organization policy contradiction engine.
* `backend/app/identity/verifier.py` — Main identity verification engine returning `IdentityResult`.
* `data/dialogues/sample_dialogues.jsonl` — 26 synthetic English dialogues dataset.
* `models/trigger_classifier/model.joblib` — Trained OneVsRest LogisticRegression model weights.
* `models/trigger_classifier/label_binarizer.joblib` — MultiLabelBinarizer encoding matrix.
* `models/trigger_classifier/metadata.json` — Training metadata.
* `scripts/train_classifier.py` — ML Classifier training script.
* `scripts/evaluate_detector.py` — Rule engine & classifier evaluation script.
* `tests/test_identity.py` — Identity & phone normalization unit test suite (6 tests).
* `tests/test_classifier.py` — ML classifier unit test suite (1 test).

### Modified Files:
* `backend/app/detection/service.py` — Updated to consume `rules.py`, `normalizer.py`, and `safe_advice.py` and output team contract schema `DetectionResult`.
* `tests/test_rules.py` — Expanded rule engine test suite (28 tests covering direct/indirect codes, remote access, payments, threats, and safe advice).

---

## 3. Input & Expected Output

### Input:
* `raw_text: str` — Spoken utterance text from ASR (`faster-whisper`).
* `phone_number: Optional[str]` — Caller phone number string (if available).
* `claimed_org_name: Optional[str]` — Organization claimed by caller (e.g., "SBI", "CBI").

### Expected Output:
* `DetectionResult`:
  * `utterance_normalized: str`
  * `utterance_redacted: str`
  * `detected_labels: List[str]`
  * `is_critical: bool` (True if SECRET_REQUEST, REMOTE_ACCESS, or PAYMENT_REQUEST)
  * `max_severity: int` (0–5)
  * `trigger_llm: bool` (True if critical or 2+ labels detected)
  * `safe_advice_detected: bool`
* `IdentityResult`:
  * `canonical_org: str` (e.g., "State Bank of India")
  * `status: str` (`VERIFIED_OFFICIAL_NUMBER`, `CLAIM_CONTRADICTS_POLICY`, `UNVERIFIED_NUMBER`, `NOT_IN_DIRECTORY`)
  * `risk_contribution: int` (0–25 score added to Risk Index)
  * `explanation: str` (Human-readable rationale for dashboard)

---

## 4. Working & Architecture

```text
Transcript Utterance
       ↓
normalizer.py (Lower casing + Redaction)
       ↓
rules.py (Deterministic Regex Matching)
       ↓
safe_advice.py (3-Layer Negation & Context Guard Filter)
       ↓
classifier.py (SentenceTransformers + Scikit-learn Logistic Regression)
       ↓
verifier.py (Phonenumbers + Seed Directory + Policy Checks)
       ↓
DetectionResult & IdentityResult Data Objects
```

### Algorithms & Models:
* **Rule Matching:** Pre-compiled regular expressions with boundary controls and case insensitivity.
* **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2` generating 384-dim sentence vectors.
* **Classifier:** `OneVsRestClassifier(LogisticRegression(class_weight='balanced'))`.
* **Phone Normalization:** `phonenumbers` (libphonenumber port) + regex prefix matcher for TRAI 160 range.

### Role in Project:
Provides **Stage 1 (Fast Protection)** of the SurakshaCall AI pipeline. Guarantees deterministic detection of critical threats in < 5ms without relying on LLM latency, while passing structured evidence objects to Ron's Orchestrator and Namit's Risk Aggregator.

---

## 5. Testing & Verification

* **Automated Unit Tests:** 38/38 unit tests passing under `pytest` (28 rules + 6 identity + 1 classifier + 3 backend session tests).
* **Execution Time:** ~3.3s total execution time.
* **Critical Recall:** 100% recall on `SECRET_REQUEST`, `REMOTE_ACCESS`, and `PAYMENT_REQUEST`.
* **False Positive Rate:** 0% false positives on legitimate banking calls and protective warnings ("Never share your OTP").

### Remaining Limitations:
* Dataset consists of 26 synthetic dialogues. Real-world noisy audio transcripts with heavy acoustic speech errors should be continuously collected in production.
