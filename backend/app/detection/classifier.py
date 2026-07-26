"""
SurakshaCall AI — Lightweight Multilingual Classifier
Owner: Lakshay
Task: L-06

Pipeline:
  Text → multilingual sentence embedding → OneVsRest logistic regression → label probabilities

Training:
  Run: python scripts/train_classifier.py

Inference:
  from backend.app.detection.classifier import predict_labels
"""
import json
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

MODEL_DIR = Path(__file__).parent.parent.parent.parent / "models" / "trigger_classifier"
MODEL_PATH      = MODEL_DIR / "model.joblib"
BINARIZER_PATH  = MODEL_DIR / "label_binarizer.joblib"
METADATA_PATH   = MODEL_DIR / "metadata.json"
THRESHOLD       = 0.35   # Default probability threshold for positive label


@dataclass
class ClassifierResult:
    labels: list[str]
    probabilities: dict[str, float]
    model_loaded: bool


def _try_load_model():
    """Load model lazily — returns None if not trained yet."""
    try:
        import joblib
        if MODEL_PATH.exists() and BINARIZER_PATH.exists():
            model = joblib.load(MODEL_PATH)
            binarizer = joblib.load(BINARIZER_PATH)
            return model, binarizer
    except Exception as e:
        import traceback
        print(f"Classifier loading error: {e}")
        traceback.print_exc()
    return None, None


_MODEL, _BINARIZER = None, None
_MODEL_LOADED = False


def _ensure_model():
    global _MODEL, _BINARIZER, _MODEL_LOADED
    if not _MODEL_LOADED:
        _MODEL, _BINARIZER = _try_load_model()
        _MODEL_LOADED = True


def predict_labels(text: str, threshold: float = THRESHOLD) -> ClassifierResult:
    """
    Predict utterance labels using the trained lightweight classifier.
    Falls back gracefully if model not yet trained.
    """
    _ensure_model()

    if _MODEL is None or _BINARIZER is None:
        # Model not trained yet — return empty (rules handle detection until then)
        return ClassifierResult(labels=[], probabilities={}, model_loaded=False)

    try:
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        embedding = embedder.encode([text])
        proba_matrix = _MODEL.predict_proba(embedding)

        # Handle OneVsRest predict_proba output shape which can be (n_samples, n_classes) or a list of arrays
        label_names = _BINARIZER.classes_
        probabilities = {}
        
        import numpy as np
        if isinstance(proba_matrix, np.ndarray) and len(proba_matrix.shape) == 2:
            for i, label in enumerate(label_names):
                probabilities[label] = float(proba_matrix[0][i])
        else:
            for i, label in enumerate(label_names):
                try:
                    probabilities[label] = float(proba_matrix[i][0][1])
                except (IndexError, TypeError):
                    probabilities[label] = float(proba_matrix[i])

        predicted = [
            label for label, prob in probabilities.items()
            if prob >= threshold
        ]

        return ClassifierResult(
            labels=predicted,
            probabilities=probabilities,
            model_loaded=True,
        )

    except Exception as e:
        import traceback
        print(f"Prediction execution error: {e}")
        traceback.print_exc()
        return ClassifierResult(labels=[], probabilities={}, model_loaded=False)
