"""
SurakshaCall AI — Synthetic Dialogue Generator
Owner: Lakshay
Task: L-02

Generates the remaining dialogues to hit the exact target:
- 80 Scam
- 60 Legitimate
- 40 Ambiguous
- 30 Safe Advice
Total: 210 dialogues

Saves to data/dialogues/sample_dialogues.jsonl
"""
import json
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "dialogues" / "sample_dialogues.jsonl"

# Read existing dialogues
existing = []
if DATA_PATH.exists():
    with open(DATA_PATH, encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                existing.append(json.loads(line))

# Count existing by category
scam_count = sum(1 for d in existing if d["is_scam"] and d["scenario"] != "AMBIGUOUS")
legit_count = sum(1 for d in existing if not d["is_scam"] and d["scenario"] not in ("AMBIGUOUS", "LEGITIMATE_BANK", "LEGITIMATE_COURIER") or d["scenario"] in ("LEGITIMATE_BANK", "LEGITIMATE_COURIER"))
ambig_count = sum(1 for d in existing if d["scenario"] == "AMBIGUOUS" and d["turns"][0]["labels"] != ["SAFE_ADVICE"])
safe_count = sum(1 for d in existing if d["turns"][0]["labels"] == ["SAFE_ADVICE"])

print(f"Existing count: Scam: {scam_count}, Legit: {legit_count}, Ambig: {ambig_count}, Safe: {safe_count}")

# ── Templates for generation ──────────────────────────────────────────────

BANKS = ["SBI", "HDFC", "ICICI", "Axis Bank", "Punjab National Bank", "Kotak Mahindra Bank", "Canara Bank", "Union Bank"]
POLICE_OFFICERS = ["Inspector Sharma", "officer from ED", "Inspector Verma", "Customs Officer Mehta", "CBI Inspector Grewal"]
AMOUNTS = ["10,000", "25,000", "50,000", "75,000", "1 lakh", "2 lakh"]
TIMEFRAMES = ["10 minutes", "15 minutes", "30 minutes", "1 hour", "2 hours"]
DEVICES = ["AnyDesk", "TeamViewer", "QuickSupport", "RustDesk"]

# 1. SCAM GENERATION
scam_dialogues = []
idx = 1
while len(scam_dialogues) < (80 - scam_count):
    bank = random.choice(BANKS)
    officer = random.choice(POLICE_OFFICERS)
    amount = random.choice(AMOUNTS)
    timeframe = random.choice(TIMEFRAMES)
    device = random.choice(DEVICES)
    
    scam_type = random.choice(["BANK_KYC", "DIGITAL_ARREST", "UPI_REFUND", "REMOTE_SUPPORT", "INVESTMENT", "JOB_FEE", "FAMILY_EMERGENCY"])
    
    if scam_type == "BANK_KYC":
        turns = [
            {"speaker": "caller", "text": f"Hello, I am calling from {bank} security. Your account will be frozen in {timeframe} due to pending verification.", "labels": ["AUTHORITY_CLAIM", "FEAR_THREAT", "URGENCY"]},
            {"speaker": "victim", "text": "How do I verify it?", "labels": ["NORMAL_SERVICE"]},
            {"speaker": "caller", "text": "I am sending a verification code to your phone. Share the code with me now.", "labels": ["SECRET_REQUEST", "URGENCY"]},
            {"speaker": "victim", "text": "Okay, checking my messages.", "labels": ["NORMAL_SERVICE"]}
        ]
    elif scam_type == "DIGITAL_ARREST":
        turns = [
            {"speaker": "caller", "text": f"This is {officer} calling. A non-bailable warrant is issued against your Aadhaar card for drug trafficking.", "labels": ["AUTHORITY_CLAIM", "FEAR_THREAT"]},
            {"speaker": "victim", "text": "This is a mistake! I haven't done anything.", "labels": ["NORMAL_SERVICE"]},
            {"speaker": "caller", "text": f"To clear your name, you must transfer a security deposit of {amount} rupees immediately to the safe government account.", "labels": ["PAYMENT_REQUEST", "URGENCY"]},
            {"speaker": "caller", "text": "Do not disconnect this call or tell anyone. You are under digital arrest.", "labels": ["ISOLATION"]}
        ]
    elif scam_type == "UPI_REFUND":
        turns = [
            {"speaker": "caller", "text": f"Good morning, I am calling from Google Pay refund team regarding your transaction.", "labels": ["AUTHORITY_CLAIM"]},
            {"speaker": "victim", "text": "What transaction?", "labels": ["NORMAL_SERVICE"]},
            {"speaker": "caller", "text": f"A refund of {amount} is pending. I have sent a UPI collect request, please approve the request to claim your refund.", "labels": ["PAYMENT_REQUEST"]},
            {"speaker": "victim", "text": "Let me open the app.", "labels": ["NORMAL_SERVICE"]}
        ]
    elif scam_type == "REMOTE_SUPPORT":
        turns = [
            {"speaker": "caller", "text": f"This is Microsoft IT support. Your computer is infected with malware.", "labels": ["AUTHORITY_CLAIM", "FEAR_THREAT"]},
            {"speaker": "victim", "text": "Oh, what should I do?", "labels": ["NORMAL_SERVICE"]},
            {"speaker": "caller", "text": f"Please install {device} on your computer immediately so we can fix it remotely.", "labels": ["REMOTE_ACCESS", "URGENCY"]},
            {"speaker": "caller", "text": "Share the access code displayed on the screen with me.", "labels": ["SECRET_REQUEST"]}
        ]
    else:
        turns = [
            {"speaker": "caller", "text": f"Congratulations! You won a cash reward of {amount}. This is from Kaun Banega Crorepati.", "labels": ["REWARD_SCARCITY"]},
            {"speaker": "victim", "text": "How do I get it?", "labels": ["NORMAL_SERVICE"]},
            {"speaker": "caller", "text": "You must pay a registration fee of 5,000 rupees immediately to process the reward.", "labels": ["PAYMENT_REQUEST", "URGENCY"]}
        ]
        
    scam_dialogues.append({
        "dialogue_id": f"gen_scam_en_{idx:03d}",
        "scenario": scam_type,
        "is_scam": True,
        "language": "en",
        "turns": turns,
        "expected_min_risk": random.randint(80, 95)
    })
    idx += 1

# 2. LEGITIMATE GENERATION
legit_dialogues = []
idx = 1
while len(legit_dialogues) < (60 - legit_count):
    bank = random.choice(BANKS)
    scam_type = random.choice(["LEGITIMATE_BANK", "LEGITIMATE_COURIER"])
    
    if scam_type == "LEGITIMATE_BANK":
        turns = [
            {"speaker": "caller", "text": f"Hello, this is {bank} fraud prevention department. We noticed a transaction of 5,000 rupees.", "labels": ["AUTHORITY_CLAIM", "NORMAL_SERVICE"]},
            {"speaker": "victim", "text": "Yes, I did that purchase.", "labels": ["NORMAL_SERVICE"]},
            {"speaker": "caller", "text": "Thank you for confirming. Remember, we never ask for your card PIN or OTP. Stay safe.", "labels": ["SAFE_ADVICE"]}
        ]
    else:
        turns = [
            {"speaker": "caller", "text": "Hello, this is BlueDart delivery service. Your courier package is out for delivery today.", "labels": ["NORMAL_SERVICE"]},
            {"speaker": "victim", "text": "What time will you arrive?", "labels": ["NORMAL_SERVICE"]},
            {"speaker": "caller", "text": "Between 3 PM and 6 PM. Please keep your government ID ready for verification.", "labels": ["NORMAL_SERVICE"]}
        ]
        
    legit_dialogues.append({
        "dialogue_id": f"gen_legit_en_{idx:03d}",
        "scenario": scam_type,
        "is_scam": False,
        "language": "en",
        "turns": turns,
        "expected_min_risk": random.randint(5, 15)
    })
    idx += 1

# 3. AMBIGUOUS GENERATION
ambig_dialogues = []
idx = 1
while len(ambig_dialogues) < (40 - ambig_count):
    turns = [
        {"speaker": "caller", "text": "Hello, did you receive an OTP from our service registration page?", "labels": ["UNKNOWN"]},
        {"speaker": "victim", "text": "Yes, I got a message with a code.", "labels": ["NORMAL_SERVICE"]},
        {"speaker": "caller", "text": "Perfect, please confirm if the registration works. No need to tell me the code.", "labels": ["SAFE_ADVICE"]}
    ]
    ambig_dialogues.append({
        "dialogue_id": f"gen_ambig_en_{idx:03d}",
        "scenario": "AMBIGUOUS",
        "is_scam": False,
        "language": "en",
        "turns": turns,
        "expected_min_risk": random.randint(15, 25)
    })
    idx += 1

# 4. SAFE ADVICE GENERATION
safe_dialogues = []
idx = 1
while len(safe_dialogues) < (30 - safe_count):
    turns = [
        {"speaker": "caller", "text": "This is a public safety announcement. Banks never ask for your CVV, PIN, or OTP over the phone.", "labels": ["SAFE_ADVICE"]},
        {"speaker": "caller", "text": "If you receive a suspicious call demanding immediate money transfers, hang up and report to cybercrime.gov.in.", "labels": ["SAFE_ADVICE"]}
    ]
    safe_dialogues.append({
        "dialogue_id": f"gen_safe_en_{idx:03d}",
        "scenario": "AMBIGUOUS",
        "is_scam": False,
        "language": "en",
        "turns": turns,
        "expected_min_risk": random.randint(2, 8)
    })
    idx += 1

# Combine and write
all_dialogues = existing + scam_dialogues + legit_dialogues + ambig_dialogues + safe_dialogues

with open(DATA_PATH, "w", encoding="utf-8") as f:
    for d in all_dialogues:
        f.write(json.dumps(d) + "\n")

print(f"Generation Complete! Total dialogues in dataset: {len(all_dialogues)}")
