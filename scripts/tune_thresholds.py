"""
Tune per-label probability thresholds on validation data.
"""
import json
import sys
from pathlib import Path

import click
import joblib
import numpy as np
from sklearn.metrics import precision_recall_curve


@click.command()
@click.option("--model-dir", default="models/trigger_classifier", help="Model directory")
@click.option("--validation", default="data/dialogues/v1.0.0/validation.jsonl", help="Validation JSONL")
@click.option("--output", default=None, help="Output thresholds JSON")
def main(model_dir, validation, output):
    model_dir = Path(model_dir)
    val_path = Path(validation)

    if not val_path.exists():
        print(f"Validation file not found: {validation}")
        print("Using default thresholds.")
        return

    model = joblib.load(model_dir / "model.joblib")
    binarizer = joblib.load(model_dir / "label_binarizer.joblib")

    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    texts, label_sets = [], []
    with open(val_path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            dialogue = json.loads(line)
            for turn in dialogue.get("turns", []):
                text = turn.get("text", "").strip()
                labels = turn.get("labels", [])
                if text and labels:
                    texts.append(text)
                    label_sets.append(labels)

    if not texts:
        print("No validation data found. Using defaults.")
        return

    X_val = embedder.encode(texts, show_progress_bar=False)
    Y_val = binarizer.transform(label_sets)
    Y_score = model.predict_proba(X_val)

    thresholds = {}
    for i, label in enumerate(binarizer.classes_):
        prec, rec, thr = precision_recall_curve(Y_val[:, i], Y_score[:, i])
        f1_scores = 2 * prec * rec / (prec + rec + 1e-10)
        best_idx = np.argmax(f1_scores)
        best_thr = thr[best_idx] if best_idx < len(thr) else 0.5
        thresholds[label] = round(float(best_thr), 3)

    output_path = Path(output or model_dir / "thresholds.json")
    with open(output_path, "w") as f:
        json.dump(thresholds, f, indent=2)
    print(f"Thresholds saved to {output_path}")
    for label, thr in sorted(thresholds.items()):
        print(f"  {label}: {thr}")


if __name__ == "__main__":
    main()
