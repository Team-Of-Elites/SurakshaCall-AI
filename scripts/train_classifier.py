"""
SurakshaCall AI — Classifier Training Script
Owner: Lakshay
Task: L-06

Run: python scripts/train_classifier.py

Reads:  data/dialogues/sample_dialogues.jsonl
Trains: sentence embedding + OneVsRest logistic regression
Saves:  models/trigger_classifier/
"""
import json
import sys
import joblib
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATA_PATH  = PROJECT_ROOT / "data" / "dialogues" / "sample_dialogues.jsonl"
MODEL_DIR  = PROJECT_ROOT / "models" / "trigger_classifier"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ── Load dataset ─────────────────────────────────────────────────────────────
print("Loading dataset...")
texts, label_sets = [], []

with open(DATA_PATH, encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        dialogue = json.loads(line)
        for turn in dialogue.get("turns", []):
            text = turn.get("text", "").strip()
            labels = turn.get("labels", [])
            if text and labels:
                filtered = [l for l in labels if l not in ("UNKNOWN", "NORMAL_SERVICE")]
                if filtered:
                    texts.append(text)
                    label_sets.append(filtered)

print(f"Loaded {len(texts)} labeled utterances.")

if len(texts) < 10:
    print("Not enough data to train. Add more dialogues first (minimum 10 labeled utterances).")
    sys.exit(1)

# ── Embed text ───────────────────────────────────────────────────────────────
print("Generating embeddings (paraphrase-multilingual-MiniLM-L12-v2)...")
from sentence_transformers import SentenceTransformer
embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
X = embedder.encode(texts, show_progress_bar=True, batch_size=32)

# ── Encode labels ────────────────────────────────────────────────────────────
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

mlb = MultiLabelBinarizer()
Y = mlb.fit_transform(label_sets)
print(f"Labels found: {list(mlb.classes_)}")

X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42
)
print(f"Train: {len(X_train)} | Test: {len(X_test)}")

# ── Train ────────────────────────────────────────────────────────────────────
print("Training OneVsRest Logistic Regression...")
clf = OneVsRestClassifier(
    LogisticRegression(max_iter=1000, class_weight="balanced", C=1.0)
)
clf.fit(X_train, Y_train)

# ── Evaluate ─────────────────────────────────────────────────────────────────
Y_pred = clf.predict(X_test)
print("\n== Evaluation on held-out test set ==")
print(classification_report(Y_test, Y_pred, target_names=mlb.classes_, zero_division=0))

# ── Save ─────────────────────────────────────────────────────────────────────
joblib.dump(clf, MODEL_DIR / "model.joblib")
joblib.dump(mlb, MODEL_DIR / "label_binarizer.joblib")

metadata = {
    "model": "OneVsRest + LogisticRegression",
    "embedder": "paraphrase-multilingual-MiniLM-L12-v2",
    "trained_at": datetime.now().isoformat(),
    "num_train_samples": len(X_train),
    "num_test_samples": len(X_test),
    "labels": list(mlb.classes_),
    "threshold": 0.35,
    "note": "Synthetic dataset only. Real-world accuracy will differ.",
}
with open(MODEL_DIR / "metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print(f"\nModel saved to {MODEL_DIR}")
print("Run: pytest tests/test_classifier.py -v to validate.")
