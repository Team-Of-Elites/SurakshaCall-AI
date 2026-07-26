"""
SurakshaCall AI — ML Classifier Tests
Owner: Lakshay
Run: pytest tests/test_classifier.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.detection.classifier import predict_labels

def test_classifier_prediction_runs():
    result = predict_labels("Please share your OTP.")
    assert result.model_loaded
    assert len(result.probabilities) > 0
    assert "SECRET_REQUEST" in result.probabilities
