from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    path: Path
    busy_timeout_ms: int = 5000
    synchronous: str = "NORMAL"
    enable_wal: bool = True
