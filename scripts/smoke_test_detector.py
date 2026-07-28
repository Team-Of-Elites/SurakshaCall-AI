"""
Quick smoke test: runs detect() on key scenarios and prints results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.detection.service import detect

TEST_CASES = [
    ("direct OTP", "Please share your OTP with me right now."),
    ("indirect code", "Tell me the six digit code you received in the message."),
    ("remote access", "Install AnyDesk and give me the code."),
    ("safe advice", "Never share your OTP with anyone."),
    ("safe advice bank", "Bank employees never ask for your PIN."),
    ("legitimate", "Your parcel will be delivered tomorrow."),
    ("authority + fear", "This is CBI. You will be arrested if you don't pay."),
    ("Hindi secret", "OTP batao jaldi."),
    ("Hindi authority", "Main CBI se bol raha hoon."),
    ("Hindi safe", "Kisi ko apna OTP mat batana."),
    ("Hindi threat", "Aapka account freeze ho jayega."),
    ("code-mixed", "Message mein jo six digit aaya hai woh bataiye."),
]


def main():
    passed = 0
    failed = 0
    for name, text in TEST_CASES:
        try:
            result = detect(text)
            labels = result.detected_labels
            level = "CRITICAL" if result.is_critical else "NORMAL"
            status = "OK"
            passed += 1
        except Exception as e:
            labels = []
            level = "ERROR"
            status = f"FAIL: {e}"
            failed += 1
        print(f"  [{level:<8}] {name:25s} -> {', '.join(labels) if labels else 'none':40s} {status}")

    total = passed + failed
    print(f"\n{total} tests: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
