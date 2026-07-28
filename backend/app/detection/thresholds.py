import json
from pathlib import Path

DEFAULT_THRESHOLDS: dict[str, float] = {
    "SECRET_REQUEST": 0.34,
    "REMOTE_ACCESS": 0.42,
    "PAYMENT_REQUEST": 0.40,
    "FEAR_THREAT": 0.45,
    "ISOLATION": 0.45,
    "AUTHORITY_CLAIM": 0.55,
    "URGENCY": 0.55,
    "SCREEN_SHARE": 0.50,
    "CHANNEL_SWITCH": 0.50,
    "REWARD_SCARCITY": 0.50,
    "PERSISTENCE": 0.55,
    "SAFE_ADVICE": 0.48,
    "NORMAL_SERVICE": 0.55,
    "UNKNOWN": 0.60,
}

_THRESHOLDS: dict[str, float] = dict(DEFAULT_THRESHOLDS)


def load_thresholds(path: str | Path) -> None:
    path = Path(path)
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        _THRESHOLDS.update(data)


def get_threshold(label: str) -> float:
    return _THRESHOLDS.get(label, 0.5)


def set_threshold(label: str, value: float) -> None:
    _THRESHOLDS[label] = value


def get_all_thresholds() -> dict[str, float]:
    return dict(_THRESHOLDS)


def save_thresholds(path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(_THRESHOLDS, f, indent=2)
