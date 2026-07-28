"""
Validate model artifact: file existence, checksums, label order, embedding revision.
"""
import json
import sys
from pathlib import Path

from backend.app.classifier.artifact import verify_artifact


def main():
    model_dir = Path(__file__).parent.parent / "models" / "trigger_classifier"
    print(f"Checking artifact at: {model_dir}")

    if not model_dir.exists():
        print("  ERROR: Directory not found")
        sys.exit(1)

    ok, errors = verify_artifact(model_dir)
    for err in errors:
        print(f"  ERROR: {err}")

    label_order_path = model_dir / "label_order.json"
    if label_order_path.exists():
        with open(label_order_path) as f:
            label_order = json.load(f)
        print(f"  Labels ({len(label_order)}): {label_order}")
    else:
        print("  WARNING: label_order.json not found")

    metadata_path = model_dir / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path) as f:
            meta = json.load(f)
        print(f"  Model: {meta.get('model', 'unknown')}")
        print(f"  Embedder: {meta.get('embedder', 'unknown')}")
        print(f"  Trained: {meta.get('trained_at', 'unknown')}")
        print(f"  Train samples: {meta.get('num_train_samples', 0)}")

    if ok:
        print("  Artifact OK")
    else:
        print("  Artifact has issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
