import joblib
from pathlib import Path
from typing import Any

_CALIBRATOR = None


def load_calibrator(path: str | Path) -> Any | None:
    global _CALIBRATOR
    path = Path(path)
    if path.exists():
        try:
            _CALIBRATOR = joblib.load(path)
            return _CALIBRATOR
        except Exception:
            pass
    return None


def calibrate_scores(raw_scores: list[float]) -> list[float]:
    if _CALIBRATOR is None:
        return raw_scores
    try:
        import numpy as np
        arr = np.array(raw_scores).reshape(-1, 1)
        calibrated = _CALIBRATOR.predict_proba(arr)
        if calibrated.shape[1] >= 2:
            return calibrated[:, 1].tolist()
        return calibrated[:, 0].tolist()
    except Exception:
        return raw_scores
