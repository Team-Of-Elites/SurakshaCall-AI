import hashlib
import json
from pathlib import Path

REQUIRED_FILES = {
    "classifier.joblib",
    "label_binarizer.joblib",
    "thresholds.json",
    "label_order.json",
    "metadata.json",
    "training_manifest.json",
}


def checksum_file(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def verify_artifact(model_dir: str | Path) -> tuple[bool, list[str]]:
    model_dir = Path(model_dir)
    errors: list[str] = []
    for fname in REQUIRED_FILES:
        fpath = model_dir / fname
        if not fpath.exists():
            errors.append(f"Missing: {fname}")

    checksums_path = model_dir / "checksums.sha256"
    if checksums_path.exists():
        with open(checksums_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("  ")
                if len(parts) == 2:
                    expected_hash, fname = parts
                    fpath = model_dir / fname
                    if fpath.exists():
                        actual = checksum_file(fpath)
                        if actual != expected_hash:
                            errors.append(f"Checksum mismatch: {fname}")
    return len(errors) == 0, errors


def generate_checksums(model_dir: str | Path) -> None:
    model_dir = Path(model_dir)
    lines: list[str] = []
    for fname in REQUIRED_FILES:
        fpath = model_dir / fname
        if fpath.exists():
            h = checksum_file(fpath)
            lines.append(f"{h}  {fname}")
    sha_path = model_dir / "checksums.sha256"
    sha_path.write_text("\n".join(lines) + "\n")
