"""
Out-of-distribution detection for classifier inputs.
Uses distance to training embedding prototypes as a simple OOD signal.
"""

from pathlib import Path
import numpy as np

_PROTOTYPES: np.ndarray | None = None
_THRESHOLD: float = 2.0


def load_prototypes(path: str | Path) -> None:
    global _PROTOTYPES
    path = Path(path)
    if path.exists():
        _PROTOTYPES = np.load(path)


def set_threshold(t: float) -> None:
    global _THRESHOLD
    _THRESHOLD = t


def is_ood(embedding: list[float]) -> tuple[bool, float]:
    if _PROTOTYPES is None or len(_PROTOTYPES) == 0:
        return False, 0.0
    emb = np.array(embedding)
    distances = np.linalg.norm(_PROTOTYPES - emb, axis=1)
    min_dist = float(np.min(distances))
    return min_dist > _THRESHOLD, min_dist
