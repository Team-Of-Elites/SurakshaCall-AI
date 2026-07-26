# Evaluation Methodology

This document outlines how we track the accuracy and performance (latency) of the SurakshaCall AI system.

## 1. Automated Tracking
During `EVALUATION` mode, the system automatically writes test results to:
`data/evaluation/latest_results.csv`

**Metrics Tracked:**
*   `audio_duration_ms`: Length of the audio clip being tested.
*   `transcript_latency_ms`: Time taken for the ASR engine to convert audio to text.
*   `fast_warning_latency_ms`: Time taken from end of speech to generating an initial UI warning.
*   `full_latency_ms`: Total time including Community Intelligence matching.
*   `expected_label` vs `actual_label`: Did the system detect the specific scam (e.g., DIGITAL_ARREST)?
*   `expected_risk` vs `actual_risk`: Did the system assign the correct severity (HIGH vs LOW)?

## 2. The Community Matcher
To evaluate the Community Intelligence engine, we run a "Held-Out" evaluation. This means we feed the system new, unseen scam transcripts and verify if the `Weighted Jaccard Similarity` algorithm correctly groups them with our known 15 seed patterns.

*   **Similarity Threshold:** A match is considered successful if the calculated similarity score is `> 0.5`.
*   **Weights:** The system prioritizes the "Requested Action" (e.g., asking for an OTP) over the "Language" spoken.

## 3. QA Checklist
For day-to-day testing, refer to `test-status.md`.