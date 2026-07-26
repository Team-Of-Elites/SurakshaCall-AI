# Identity Verification Module — SurakshaCall AI

**Owner:** Lakshay  
**Role:** Phone Number Normalization & Organization Identity Verification  

---

## 1. Overview & Objective
The Identity Verification Module validates caller identity claims against official organization databases, normalizes Indian phone numbers, checks TRAI 160-series commercial call ranges, and detects policy contradictions (e.g., caller claiming to be CBI demanding money transfers).

---

## 2. Component Files
* `phone_numbers.py` — Integrates `phonenumbers` library to parse, format E.164 numbers, detect mobile/VoIP types, and identify TRAI 160 commercial ranges.
* `aliases.py` — Maps organization name variations (e.g., "sbi", "state bank") to canonical directory entry names ("State Bank of India").
* `policy_checks.py` — Contains official published policy rules for banks and law enforcement to flag immediate policy violations.
* `verifier.py` — Main verification engine function `verify_identity()` that loads `data/trusted_directory/seed.json` and produces `IdentityResult`.

---

## 3. Input & Expected Output

### Input:
* `phone_number: Optional[str]` — Caller phone number string.
* `claimed_org_name: Optional[str]` — Organization claimed by caller.
* `detected_labels: List[str]` — Labels detected by `rules.py`.

### Expected Output (`IdentityResult`):
* `raw_number: Optional[str]`
* `phone_info: PhoneInfo`
* `claimed_org: Optional[str]`
* `canonical_org: Optional[str]`
* `status: str` (`VERIFIED_OFFICIAL_NUMBER`, `CLAIM_CONTRADICTS_POLICY`, `UNVERIFIED_NUMBER`, `ORGANIZATION_NOT_IN_DIRECTORY`)
* `in_trusted_directory: bool`
* `policy_contradiction: Optional[str]`
* `risk_contribution: int` (0 to 25 score added to Risk Index)
* `explanation: str` (Human-readable rationale)

---

## 4. Internal Workflow & Data Flow
```text
Phone Number + Claimed Org + Labels 
    ↓
phone_numbers.py (E.164 normalization + TRAI check)
    ↓
aliases.py (Canonical name lookup)
    ↓
policy_checks.py (Published policy contradiction check)
    ↓
verifier.py (Seed directory lookup & Risk Contribution calculation)
    ↓
IdentityResult
```

---

## 5. Testing & Verification
* **Unit Tests:** `tests/test_identity.py` (6 tests passing).
* **Test Coverage:** Covers valid Indian mobiles, invalid formats, TRAI 160 numbers, verified official numbers, spoof risks, and CBI policy contradiction.
