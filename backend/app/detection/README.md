# Detection Module — SurakshaCall AI

**Owner:** Lakshay  
**Role:** Fast Stage 1 Safety Layer (Deterministic Rules & ML Classifier)  

---

## 1. Overview & Objective
The Detection Module provides immediate, low-latency identification of scam threats and psychological manipulation tactics from spoken transcript utterances. It operates before deep LLM reasoning to ensure critical threats (such as OTP requests, payment demands, and remote access software installation) are flagged instantaneously.

---

## 2. Component Files
* `labels.py` — Taxonomy of 14 utterance-level labels, 11 scenario-level labels, severity mapping (0–5), and critical label sets.
* `rules.py` — Deterministic English regular expression rule engine (30+ rules covering `SECRET_REQUEST`, `PAYMENT_REQUEST`, `REMOTE_ACCESS`, `ISOLATION`, `AUTHORITY_CLAIM`, `FEAR_THREAT`, `URGENCY`, `SCREEN_SHARE`).
* `normalizer.py` — Transcript casing normalization and PII redaction (`[CODE]`, `[PHONE]`, `[PAN]`, `[AADHAAR]`, `[EMAIL]`).
* `safe_advice.py` — 3-layer guard filter preventing false alarms on protective statements (e.g., "Never share your OTP", "Bank officers will never ask").
* `classifier.py` — Multilingual ML classifier wrapper using `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`) and `scikit-learn` `OneVsRestClassifier(LogisticRegression)`.
* `service.py` — Main entry point function `detect(raw_text)` returning the team API contract object `DetectionResult`.

---

## 3. Input & Expected Output

### Input:
* `raw_text: str` — ASR transcript utterance.
* `language: Optional[str]` — Language ISO code (default `"en"`).

### Expected Output (`DetectionResult`):
* `utterance_normalized: str` — Cleaned text.
* `utterance_redacted: str` — Redacted text for privacy logging.
* `events: List[dict]` — Detailed rule match quotes and confidence.
* `detected_labels: List[str]` — All matched labels.
* `is_critical: bool` — True if `SECRET_REQUEST`, `REMOTE_ACCESS`, or `PAYMENT_REQUEST` detected.
* `max_severity: int` — Highest severity score (0 to 5).
* `trigger_llm: bool` — True if critical event or 2+ labels detected.
* `safe_advice_detected: bool` — True if protective filter engaged.

---

## 4. Internal Workflow & Data Flow
```text
ASR Utterance → normalizer.py → rules.py → safe_advice.py → classifier.py → DetectionResult
```

---

## 5. Testing & Verification
* **Unit Tests:** `tests/test_rules.py` (28 tests), `tests/test_classifier.py` (1 test).
* **Evaluation:** `scripts/evaluate_detector.py` showing 100% recall on critical events.
