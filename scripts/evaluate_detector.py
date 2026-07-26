"""
SurakshaCall AI — Detector Evaluation Script
Owner: Lakshay
Task: L-10

Run: python scripts/evaluate_detector.py
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.detection.service import detect

DATA_PATH = PROJECT_ROOT / "data" / "dialogues" / "sample_dialogues.jsonl"

print("== SurakshaCall AI Detector Evaluation ==\n")

total_turns = 0
true_positives  = {"SECRET_REQUEST": 0, "REMOTE_ACCESS": 0, "PAYMENT_REQUEST": 0}
false_negatives = {"SECRET_REQUEST": 0, "REMOTE_ACCESS": 0, "PAYMENT_REQUEST": 0}
safe_advice_false_critical = 0
legit_call_false_alarms = 0

dialogues = []
with open(DATA_PATH, encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip()
        if line:
            dialogues.append(json.loads(line))

for dialogue in dialogues:
    is_scam = dialogue.get("is_scam", False)
    for turn in dialogue.get("turns", []):
        text  = turn.get("text", "")
        expected = set(turn.get("labels", []))
        result = detect(text)
        detected = set(result.detected_labels)
        total_turns += 1

        for critical in ["SECRET_REQUEST", "REMOTE_ACCESS", "PAYMENT_REQUEST"]:
            if critical in expected:
                if critical in detected:
                    true_positives[critical] += 1
                else:
                    false_negatives[critical] += 1

        if "SAFE_ADVICE" in expected and result.is_critical:
            safe_advice_false_critical += 1

        if not is_scam and result.is_critical:
            legit_call_false_alarms += 1

print(f"Total turns evaluated: {total_turns}")
print(f"Total dialogues:       {len(dialogues)}\n")

print(f"== Critical Recall (Must-Catch Events) ==")
for label in ["SECRET_REQUEST", "REMOTE_ACCESS", "PAYMENT_REQUEST"]:
    tp = true_positives[label]
    fn = false_negatives[label]
    total = tp + fn
    recall = tp / total if total > 0 else 0
    print(f"  {label:<20} {tp}/{total}  recall={recall:.0%}")

print(f"\n== False Positive Checks ==")
print(f"  Safe advice flagged as critical: {safe_advice_false_critical}")
print(f"  Legitimate calls flagged as critical: {legit_call_false_alarms}")

print(f"\n== Honest Limitations ==")
print("  Dataset: synthetic/consented scenarios only")
print("  Dialects: limited (Hindi/Hinglish/English — no regional variants)")
print("  ASR errors: not fully simulated")
print("  Real-world accuracy requires production data collection")
