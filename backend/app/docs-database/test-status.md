# QA Board

This document tracks the status of regression tests and specific scenarios as defined by the project requirements.

## Test Scenario Template

When running a regression test, copy and paste this template and fill out the details:

```text
Scenario: [e.g., Bank KYC, Digital Arrest, UPI Refund]
Commit: [Git commit hash or branch name]
Date: [YYYY-MM-DD]
Input mode: [e.g., Prerecorded WAV replay, Live microphone]
Whisper model: [e.g., small, base, medium]
Local LLM: [e.g., Llama 3 8B, None]
Expected risk: [e.g., HIGH, MODERATE, LOW]
Actual risk: [What the system calculated]
Fast warning latency: [ms from phrase end to rule match]
Full decision latency: [ms from phrase end to LLM result]
Correct evidence: [List correctly extracted intents/tactics]
False evidence: [List incorrectly extracted intents/tactics]
Result: [PASS / FAIL]
Open issue: [Link to issue or description if FAIL]
Owner: [Name of tester]
```

## Scenarios Tracked (Day-by-Day)

### [Scenario: Bank KYC]
*Will be updated post Day-5.*

### [Scenario: Digital Arrest]
*Will be updated post Day-5.*

### [Scenario: UPI Refund]
*Will be updated post Day-5.*

### [Scenario: Remote Support]
*Will be updated post Day-5.*

### [Scenario: Courier / Customs]
*Will be updated post Day-5.*

### [Scenario: Legitimate Courier]
*Will be updated post Day-5.*

### [Scenario: Legitimate Safety Advice]
*Will be updated post Day-5.*

### [Scenario: Database Unavailable]
*Will be updated post Day-10.*
