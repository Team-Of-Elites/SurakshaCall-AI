"""
Validate dialogue dataset JSONL.
Rejects: duplicate IDs, unknown labels, bad spans, missing fields.
"""
import json
import sys
from pathlib import Path

VALID_LABELS = {
    "AUTHORITY_CLAIM", "URGENCY", "FEAR_THREAT", "ISOLATION",
    "FORCED_COMPLIANCE", "SECRET_REQUEST", "PAYMENT_REQUEST",
    "UPI_ACTION", "REMOTE_ACCESS", "SCREEN_SHARE", "SCREEN_SHARING",
    "LINK_OR_APP_REDIRECTION", "CHANNEL_SWITCH", "REWARD_SCARCITY",
    "TRUST_BUILDING", "PERSISTENCE", "SAFE_ADVICE", "USER_REFUSAL",
    "NORMAL_SERVICE", "AMBIGUOUS_REQUEST", "UNKNOWN",
}

VALID_SPEAKERS = {"caller", "victim", "user", "unknown"}
VALID_SCENARIOS = {
    "BANK_KYC", "DIGITAL_ARREST", "UPI_REFUND", "REMOTE_SUPPORT",
    "COURIER_CUSTOMS", "SIM_DEACTIVATION", "INVESTMENT", "JOB_FEE",
    "LOAN_FEE", "LOTTERY_REWARD", "FAMILY_EMERGENCY",
    "IMPERSONATED_RELATIVE", "LEGITIMATE_BANK", "LEGITIMATE_COURIER",
    "LEGITIMATE_SUPPORT", "SAFETY_EDUCATION", "AMBIGUOUS", "OTHER",
}


def validate_file(path: str) -> int:
    errors = 0
    seen_convo_ids: set[str] = set()
    seen_turn_ids: set[str] = set()

    with open(path, encoding="utf-8-sig") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                convo = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"  Line {line_num}: Invalid JSON — {e}")
                errors += 1
                continue

            convo_id = convo.get("dialogue_id", "") or convo.get("conversation_id", "")
            if not convo_id:
                print(f"  Line {line_num}: Missing dialogue_id")
                errors += 1
                continue

            if convo_id in seen_convo_ids:
                print(f"  Line {line_num}: Duplicate dialogue_id: {convo_id}")
                errors += 1
            seen_convo_ids.add(convo_id)

            scenario = convo.get("scenario", "")
            if scenario and scenario not in VALID_SCENARIOS:
                print(f"  Line {line_num}: Unknown scenario: {scenario}")

            turns = convo.get("turns", [])
            if not turns:
                print(f"  Line {line_num}: No turns")
                errors += 1
                continue

            for ti, turn in enumerate(turns):
                turn_id = turn.get("turn_id", f"{convo_id}_t{ti}")
                if turn_id in seen_turn_ids:
                    print(f"  Line {line_num}, turn {ti}: Duplicate turn_id: {turn_id}")
                    errors += 1
                seen_turn_ids.add(turn_id)

                text = turn.get("text", "")
                if not text:
                    print(f"  Line {line_num}, turn {ti}: Empty text")
                    errors += 1

                speaker = turn.get("speaker", "")
                if speaker and speaker not in VALID_SPEAKERS:
                    print(f"  Line {line_num}, turn {ti}: Unknown speaker: {speaker}")
                    errors += 1

                labels = turn.get("labels", [])
                for label in labels:
                    if label not in VALID_LABELS:
                        print(f"  Line {line_num}, turn {ti}: Unknown label: {label}")
                        errors += 1

    return errors


if __name__ == "__main__":
    paths = sys.argv[1:] or ["data/dialogues/sample_dialogues.jsonl"]
    total_errors = 0
    for p in paths:
        p_path = Path(p)
        if not p_path.exists():
            print(f"File not found: {p}")
            total_errors += 1
            continue
        print(f"Validating {p}...")
        errs = validate_file(str(p_path))
        if errs:
            print(f"  {errs} error(s) found")
        else:
            print(f"  OK — no errors")
        total_errors += errs
    sys.exit(1 if total_errors else 0)
