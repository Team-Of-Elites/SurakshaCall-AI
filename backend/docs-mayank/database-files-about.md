# Deep Dive: The Database Layer of SurakshaCall AI

This document provides a deeper look into the four core files we built for the database. If you need to understand exactly *how* the code works under the hood so you can explain it to the judges or your team, this is your guide.

---

## 1. `schema.sql` (The Blueprint)
**Location:** `backend/app/database/schema.sql`

This file is written in SQL (Structured Query Language). It acts as the blueprint for our database, telling SQLite exactly what tables to create and what columns each table has.

### Key Concepts in our Schema:
*   **`CREATE TABLE IF NOT EXISTS`**: This command tells SQLite to create a table, but *only* if it doesn't already exist. This prevents errors if we run the script twice.
*   **`PRIMARY KEY`**: Every table has a column (usually `id` or `number`) marked as the Primary Key. This means every row must have a unique value in this column. It's like an Aadhar number for that specific row of data.
*   **`FOREIGN KEY`**: This is how we link tables together. For example, in the `utterances` table, we have `FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE`. 
    *   *What it means:* An utterance *must* belong to a valid session. If a session is deleted, `ON DELETE CASCADE` ensures all connected utterances are automatically deleted too, preventing "orphan" data.
*   **Privacy Built-In**: Look at the `sessions` table. Instead of `caller_number`, we named the column `caller_number_redacted`. This explicitly reminds anyone working on the code that raw phone numbers should not be saved here. Similarly, `utterances` uses `text_redacted`.

---

## 2. `connection.py` (The Gateway)
**Location:** `backend/app/database/connection.py`

This Python file acts as the gateway between our backend code and the actual SQLite database file on the hard drive.

### Deep Dive into the Code:
*   **`DATABASE_PATH = DATA_DIR / "suraksha.db"`**: We use Python's `pathlib` to dynamically find where the `data/` folder is, ensuring the database is always saved in the right place, no matter whose computer runs the code.
*   **`conn = sqlite3.connect(DATABASE_PATH)`**: This is the built-in Python command to open the database file. If the file doesn't exist, SQLite creates it automatically.
*   **`conn.row_factory = sqlite3.Row`**: By default, SQLite returns data as "tuples" (like `row[0]`, `row[1]`). Setting this factory allows us to access data like a Python dictionary (`row['session_id']`). This makes the code much easier to read!
*   **`conn.execute("PRAGMA foreign_keys = ON;")`**: *Crucial step.* By default, SQLite ignores Foreign Key rules (for backwards compatibility reasons). We forcefully turn it `ON` so our strict relationship rules (like deleting utterances when a session is deleted) actually work.

---

## 3. `seed.py` (The Builder)
**Location:** `backend/app/database/seed.py`

This script initializes the database and fills it with dummy data. It's what you run in the terminal.

### Deep Dive into the Code:
*   **`argparse` module**: We use this to allow terminal commands like `--reset`. The script checks if `--reset` was typed; if so, it triggers `os.remove(DATABASE_PATH)` to literally delete the `.db` file before rebuilding it.
*   **`conn.executescript(schema_script)`**: This reads the entire `schema.sql` file and runs all the commands at once to build the empty tables.
*   **`conn.executemany(...)`**: When inserting the trusted organizations, we pass a list of organizations to `executemany()`. This is much faster and safer than inserting them one by one in a loop.
*   **The `patterns` list**: This is a list of Python dictionaries. The script loops through them and uses `json.dumps()` to turn lists (like `["AUTHORITY", "URGENCY"]`) into text strings, because SQLite doesn't have a native "List" or "Array" data type.

---

## 4. `repositories.py` (The Operations Room)
**Location:** `backend/app/database/repositories.py`

A "Repository" is a design pattern. Instead of letting your application code (like the AI models or APIs) write raw SQL queries, they ask the Repository to do it for them.

### Deep Dive into the Code:
*   **Parameterized Queries (`?`)**: Look at how we insert data:
    ```python
    conn.execute("INSERT INTO sessions (id, ...) VALUES (?, ...)", (session_id, ...))
    ```
    Notice we use `?` instead of directly putting the `session_id` into the string. This is called a *parameterized query*. It is the ultimate defense against **SQL Injection attacks**. It forces SQLite to treat the input as pure data, not executable code.
*   **`_get_utc_now_str()`**: Databases should always store time in UTC (Universal Time Coordinated) to avoid timezone bugs. This helper function generates a strict, standard timestamp (ISO format) every time a session is created or risk is recorded.
*   **`conn.commit()`**: When you `INSERT` or `UPDATE` data, it initially only happens in memory. You *must* call `conn.commit()` to permanently save those changes to the `suraksha.db` file.
*   **Returning Dictionaries**: After saving to the database, functions like `create_session` return a Python dictionary of the data. This allows the rest of the backend to immediately use that data without having to query the database again.

---

## 5. The Privacy Engine (`backend/app/privacy/`)
**Location:** The `backend/app/privacy` folder contains `redaction.py`, `retention.py`, and `status.py`.

This layer acts as the absolute security guard *before* data ever touches the Database Layer.

### Deep Dive into the Code:
*   **`redaction.py` (The Scrubber)**: Uses "Regular Expressions" (regex) to hunt down patterns like `[A-Z]{5}[0-9]{4}[A-Z]{1}` (which is the exact format of an Indian PAN card) and forcefully replaces it with `[PAN_REDACTED]`. It uses an ordered list so that a 12-digit Aadhaar card isn't accidentally scrubbed as a 4-digit OTP first.
*   **`retention.py` (The Rules)**: An Enum setup that dictates whether we are in `MAXIMUM_PRIVACY` or `EVALUATION`. If we are in `MAXIMUM_PRIVACY`, it explicitly returns `False` for `should_save_transcript()`, which tells the `repositories.py` to completely ignore save requests. 
*   **`status.py` (The Proof)**: Generates a JSON payload confirming `raw_audio_saved: False`. This is essential because the Frontend UI (built by Palak) needs a way to visually display a green "Privacy Safe" checkmark to users and judges.

---

## 6. The Community Intelligence Engine (`backend/app/community/`)
**Location:** The `backend/app/community` folder contains the algorithm that figures out if a live call is a known scam.

### Deep Dive into the Code:
*   **`fingerprint.py` (The Blueprint)**: A Pydantic model that defines the exact shape of a scam pattern (Tactics, Organization, Threat Type).
*   **`weights.py` (The Rules)**: Assigns points to different parts of the scam. For example, if both the live call and the database pattern ask for an "OTP" (Requested Action), that is worth 4 points. If they just use the same "Language", that is only worth 1 point.
*   **`matcher.py` (The Calculator)**: Implements a "Weighted Jaccard Similarity" algorithm. It compares a live fingerprint against a known database fingerprint and outputs a percentage score (e.g., 0.85 or 85% match).
*   **`service.py` (The Orchestrator)**: Connects everything. It grabs all 15 known scams from SQLite, runs them through the `matcher.py`, and returns the highest scoring threat.

---

## 7. The Cleanup Protocol (`cleanup.py`)
**Location:** `backend/app/database/cleanup.py`

This script executes when a call ends. It calls `end_session()` to mark the session as finished, and if the system is in `MAXIMUM_PRIVACY` mode, it aggressively executes a `DELETE FROM utterances` SQL command to guarantee no unredacted memory slipped through to the hard drive.
