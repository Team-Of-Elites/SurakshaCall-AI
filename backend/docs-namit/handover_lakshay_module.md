# Handoff Documentation: Lakshay's Stage 1 Safety & Identity Verification Module

Hi Team,

I have completed and verified my entire task ownership (Tasks L-01 to L-10). The code is fully functional, tested, and ready to be integrated into the backend pipeline.

Here is a summary of what has been built, where the files are, and how you can consume them in your modules.

---

## 📁 1. Directory & File Locations

All my work is isolated inside these specific directories:

### Detection Module (Fast Stage 1 Alerts)
*   `backend/app/detection/labels.py` — Utterance and scenario label taxonomies.
*   `backend/app/detection/normalizer.py` — Clean casing normalizer and PII redaction.
*   `backend/app/detection/rules.py` — Deterministic regex rules matching dangerous requests.
*   `backend/app/detection/safe_advice.py` — 3-layer guard filter to prevent false warnings on advice.
*   `backend/app/detection/classifier.py` — ML classifier loading & prediction logic.
*   `backend/app/detection/service.py` — Main entry point contract.

### Identity Verification Module
*   `backend/app/identity/phone_numbers.py` — Phonenumbers normalizer and TRAI 160-series matcher.
*   `backend/app/identity/aliases.py` — Canonical alias mapper for banks/authorities.
*   `backend/app/identity/policy_checks.py` — Verifies actions against official published policies.
*   `backend/app/identity/verifier.py` — Main verifier loading `seed.json` directory.

### Scripts, Models & Dataset
*   `scripts/generate_synthetic_dialogues.py` — Dataset expansion script.
*   `scripts/train_classifier.py` — ML model training pipeline.
*   `scripts/evaluate_detector.py` — Precision, recall, and false alarm metrics reporting script.
*   `data/dialogues/sample_dialogues.jsonl` — Labeled dataset containing exactly **210 dialogues** (80 scam, 60 legitimate, 40 ambiguous, 30 safe advice).
*   `models/trigger_classifier/` — Saved model binaries (`model.joblib`, `label_binarizer.joblib`).

---

## 🚀 2. How to Use My Module (API Contracts)

You can import and consume the Stage 1 output inside your orchestrator engines using these two clean entry points:

### A. Stage 1 Text Detection (For Ron & Odil)
Use `detect(raw_text)` to check every transcript turn. It runs casing normalization, redacts credentials, runs regex checks, checks safe advice context, and runs ML model inference.

```python
from backend.app.detection.service import detect

# 1. Feed the raw speech transcript turn
result = detect("Please share your OTP code immediately.")

# 2. Extract structured flags
print(result.detected_labels)      # Output: ['SECRET_REQUEST']
print(result.is_critical)          # Output: True (Trigger warning)
print(result.trigger_llm)          # Output: True (Passes warning to Stage 2 LLM)
print(result.utterance_redacted)   # Output: "please share your [CODE] immediately."
```

### B. Identity Verification Engine (For Ron & Namit)
Use `verify_identity(phone_number, claimed_org_name, detected_labels)` to check calling numbers against the trusted directory, check for spoof indicators (VoIP), and flag policy contradictions.

```python
from backend.app.identity.verifier import verify_identity

# 1. Run the identity validator
identity = verify_identity(
    phone_number="1800112211",
    claimed_org_name="SBI",
    detected_labels=["NORMAL_SERVICE"]
)

# 2. Extract verification details
print(identity.status)             # Output: VERIFIED_OFFICIAL_NUMBER
print(identity.risk_contribution)  # Output: 0 (No risk added)
print(identity.canonical_org)      # Output: "State Bank of India"
print(identity.explanation)        # Output: "Calling number matches a known official number..."
```

---

## 🧪 3. Running My Unit Tests

I have written 35 automated tests verifying every edge case. You can run them to verify my module behaves correctly on your local machine:
```bash
python -m pytest tests/test_rules.py tests/test_identity.py tests/test_classifier.py -v
```

Let me know if you have any questions during integration!
