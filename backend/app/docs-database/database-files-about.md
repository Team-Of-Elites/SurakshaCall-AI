# The Database & Intelligence Layer (Mayank's Work)

This document explains everything Mayank built for the SurakshaCall AI backend. 

**Part 1** is a quick cheat sheet you can use to explain your work to your team or the judges.
**Part 2** is a technical deep-dive into the code for when you need to answer specific engineering questions.

---

## PART 1: The Cheat Sheet (How to explain your work)

Use these talking points when presenting your contribution to the project:

### 1. The Database Setup (`schema.sql` & `connection.py`)
*   **What you built:** The foundation of where the AI's memory lives. 
*   **How to explain it:** *"I built our local SQLite database. I wrote the SQL blueprint (`schema.sql`) to define where we store active calls and detected risks. I also built the Python connection layer (`connection.py`), which forcefully turns on 'Foreign Keys'. This ensures that if a call session is deleted, all the transcripts attached to it are automatically deleted too—preventing orphaned data."*

### 2. The Database Builder (`seed.py`)
*   **What you built:** A terminal script to instantly create or wipe the database.
*   **How to explain it:** *"I wrote the `seed.py` script so we never have to build the database manually. If you run it with `--reset`, it completely nukes the old database and rebuilds a fresh one pre-loaded with our 15 known mock scams (like 'Digital Arrest') and our trusted banks (like SBI). It’s perfect for getting a clean slate right before our final presentation."*

### 3. The SQL Hider (`repositories.py`)
*   **What you built:** A middleman so the AI code never touches raw SQL.
*   **How to explain it:** *"I built the 'Repository Layer'. The rest of your AI code shouldn't be writing messy SQL. Instead, when the AI detects a scam, it just calls my `add_risk_snapshot()` Python function, and my code safely handles the SQL using 'Parameterized Queries' (the `?` symbol) to completely block hackers from attempting SQL injection."*

### 4. The Privacy Scrubber (`backend/app/privacy/`)
*   **What you built:** The absolute security guard before data is saved.
*   **How to explain it:** *"I built a regex-powered Redaction Engine. Before any transcript is allowed to be saved to my database, my code intercepts it and scrubs out things like 12-digit Aadhaar numbers, PAN cards, and OTPs, replacing them with safe tags like `[AADHAAR_REDACTED]`. We can prove to the judges that we never store private financial data."*

### 5. The Threat Detective (`backend/app/community/`)
*   **What you built:** The algorithm that compares a live call to known scams.
*   **How to explain it:** *"I built the Community Intelligence Matcher. When the AI analyzes a live call, my code compares the caller's tactics against our 15 known database scams using a 'Weighted Jaccard' math formula. I programmed it so that asking for an OTP is weighted at 4 points, but speaking Hindi is only 1 point. If the match score is over 50%, we flag it."*

### 6. The Session Cleaner (`cleanup.py`)
*   **What you built:** The script that sweeps up after a call ends.
*   **How to explain it:** *"When a phone call hangs up, my `cleanup.py` script triggers. If we are in 'Maximum Privacy' mode, it automatically triggers a hard DELETE command in the database to wipe out any leftover memory buffers. It ensures we leave zero trace behind."*

### 7. The Automated Proof (`tests/`)
*   **What you built:** The Quality Assurance (QA) math checks.
*   **How to explain it:** *"To meet our strict definition of done, I wrote three `pytest` scripts. They run completely invisible, in-memory databases to mathematically prove our privacy scrubber works and our threat-matching algorithm calculates scores correctly without needing to run a live audio call."*

---
---

## PART 2: Technical Deep Dive (For Engineering Questions)

If the judges ask specific technical questions about *how* the code works, refer to these points.

### 1. `schema.sql` (The Blueprint)
*   **`CREATE TABLE IF NOT EXISTS`**: Tells SQLite to create a table only if it doesn't already exist. Prevents errors on multiple runs.
*   **`FOREIGN KEY`**: How we link tables. For example, `FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE`. If a session is deleted, `ON DELETE CASCADE` automatically deletes all connected utterances.
*   **Privacy Built-In**: Instead of `caller_number`, we named the column `caller_number_redacted` to remind developers not to save raw numbers.

### 2. `connection.py` (The Gateway)
*   **`DATABASE_PATH = DATA_DIR / "suraksha.db"`**: Uses Python's `pathlib` to dynamically find the `data/` folder, ensuring the DB is saved in the right place on any computer.
*   **`conn.row_factory = sqlite3.Row`**: Allows us to access data like a Python dictionary (`row['session_id']`) instead of tuples (`row[0]`).
*   **`conn.execute("PRAGMA foreign_keys = ON;")`**: SQLite ignores Foreign Key rules by default. We forcefully turn it `ON` so our strict relationship rules actually work.

### 3. `seed.py` (The Builder)
*   **`argparse`**: Allows terminal commands like `--reset`, which triggers `os.remove(DATABASE_PATH)` to literally delete the `.db` file before rebuilding it.
*   **`conn.executemany(...)`**: Used to insert trusted organizations in bulk, which is much faster and safer than inserting them one by one in a loop.
*   **`json.dumps()`**: SQLite doesn't have a "List" data type. We use JSON to turn lists (like `["AUTHORITY", "URGENCY"]`) into text strings for storage.

### 4. `repositories.py` (The Operations Room)
*   **Parameterized Queries (`?`)**: Example: `conn.execute("INSERT INTO sessions VALUES (?, ...)", (session_id, ...))`. This is the ultimate defense against SQL Injection attacks. It forces SQLite to treat the input as pure data, not executable code.
*   **`_get_utc_now_str()`**: Stores time in UTC (Universal Time Coordinated) to avoid timezone bugs.
*   **`conn.commit()`**: `INSERT` commands only happen in memory until you call `.commit()`, which permanently saves changes to the `.db` file.

### 5. The Privacy Engine (`backend/app/privacy/`)
*   **`redaction.py` (The Scrubber)**: Uses Regular Expressions (regex) to hunt down patterns like `[A-Z]{5}[0-9]{4}[A-Z]{1}` (exact format of an Indian PAN card) and forcefully replaces it with `[PAN_REDACTED]`. The order matters so a 12-digit Aadhaar card isn't accidentally scrubbed as a 4-digit OTP first.
*   **`retention.py` (The Rules)**: An Enum setup dictating `MAXIMUM_PRIVACY` or `EVALUATION`. In `MAXIMUM_PRIVACY`, it returns `False` for `should_save_transcript()`, explicitly telling `repositories.py` to ignore save requests. 
*   **`status.py` (The Proof)**: Generates a JSON payload confirming `raw_audio_saved: False` for the Frontend UI.

### 6. The Community Intelligence Engine (`backend/app/community/`)
*   **`fingerprint.py` (The Blueprint)**: A Pydantic model that defines the exact shape of a scam pattern.
*   **`weights.py` (The Rules)**: Assigns points to different parts of the scam. (e.g., Requested Action = 4 points, Language = 1 point).
*   **`matcher.py` (The Calculator)**: Implements the "Weighted Jaccard Similarity" algorithm to output a percentage score (e.g., 0.85 match).
*   **`service.py` (The Orchestrator)**: Grabs all 15 known scams from SQLite, runs them through the `matcher.py`, and returns the highest scoring threat.

### 7. The Cleanup Protocol (`cleanup.py`)
*   This script executes when a call ends. It calls `end_session()` to mark the session as finished. If in `MAXIMUM_PRIVACY` mode, it aggressively executes a `DELETE FROM utterances` SQL command to guarantee no unredacted memory slipped through to the hard drive.

### 8. Automated Tests (`tests/`)
*   **`test_privacy.py`**: Feeds raw Aadhaar, PAN, and OTP numbers into the `Redactor` engine. Mathematically asserts the raw numbers do *not* exist in the output text.
*   **`test_matcher.py`**: Runs fake "Community Fingerprints" through the Weighted Jaccard algorithm to ensure identical fingerprints score a perfect 1.0.
*   **`test_database.py`**: Boots up a temporary SQLite database in RAM (`:memory:`). Proves our SQL commands work perfectly without ever messing up our real `suraksha.db` file.
