import hashlib
from pathlib import Path

_CACHE_DIR = Path.home() / ".cache" / "surakshacall" / "embeddings"


def _cache_key(text: str, model_revision: str) -> str:
    raw = f"{text}::{model_revision}"
    return hashlib.sha256(raw.encode()).hexdigest()


class EmbeddingRuntime:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self._model = None
        self._cache: dict[str, list[float]] = {}

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        self._load()
        embeddings = self._model.encode(texts, show_progress_bar=False, batch_size=32)
        return embeddings.tolist()

    def encode_single(self, text: str) -> list[float]:
        return self.encode([text])[0]
