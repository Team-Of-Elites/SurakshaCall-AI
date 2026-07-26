# Privacy Mode Agreement

This document outlines the strict privacy boundaries and guarantees for the SurakshaCall AI prototype.

## The Guarantee
> Conversation audio is captured by the local laptop microphone or played from a consented test recording. Raw audio is held only in a short in-memory buffer and is not saved by default. Speech recognition and scam analysis run locally on the demonstration laptop.

## Data Handling Rules

### Raw Audio
- **Storage:** In-memory ring buffer only.
- **Persistence:** Never saved to disk or database. 
- **Duration:** Kept only as long as required for utterance chunking (typically max 20 seconds).

### Transcripts
- **Unredacted Transcripts:** Held in memory for immediate analysis (rules and local ML classifiers). Never written to the database.
- **Redacted Transcripts:** Can optionally be persisted into the `utterances` database table for evaluation purposes ONLY when `transcript_retention_enabled` is set to 1. All Personal Identifiable Information (PII), such as OTPs, account numbers, and passwords, MUST be scrubbed before saving.

### Identity and Fingerprints
- **Community Fingerprints:** Do not contain raw audio, victim details, numbers, or specific names. They consist entirely of structural metadata (tactics, organization claims, threat types).
- **Match Data:** Represents structural similarity between events.

### Session Lifecycle
- Upon session completion or system reset, all private buffers and unredacted memories are wiped. 
- Offline reset commands (e.g. `seed.py --reset`) permanently delete the entire local database file.
