from typing import Literal

from backend.app.detection.schemas import DetectorError


def invalid_transcript(detail: str = "Transcript text is empty or malformed.") -> DetectorError:
    return DetectorError(
        code="INVALID_TRANSCRIPT",
        recoverable=True,
        user_safe_message=detail,
    )


def rules_unavailable(detail: str = "Rule engine failed to load.") -> DetectorError:
    return DetectorError(
        code="RULES_UNAVAILABLE",
        recoverable=True,
        user_safe_message="Fast safety rules are temporarily unavailable. Continuing with model only.",
    )


def model_unavailable(detail: str = "Classifier model not loaded.") -> DetectorError:
    return DetectorError(
        code="MODEL_UNAVAILABLE",
        recoverable=True,
        user_safe_message="AI classifier is unavailable. Running in rules-only mode.",
    )


def model_artifact_mismatch(detail: str = "Model artifact checksum or label order mismatch.") -> DetectorError:
    return DetectorError(
        code="MODEL_ARTIFACT_MISMATCH",
        recoverable=False,
        user_safe_message="Model version mismatch. Running in rules-only mode.",
    )


def identity_data_unavailable(detail: str = "Identity directory could not be loaded.") -> DetectorError:
    return DetectorError(
        code="IDENTITY_DATA_UNAVAILABLE",
        recoverable=True,
        user_safe_message="Identity verification is temporarily unavailable.",
    )


def internal_error(detail: str = "Unexpected detector error.") -> DetectorError:
    return DetectorError(
        code="INTERNAL_ERROR",
        recoverable=False,
        user_safe_message="An unexpected error occurred during analysis.",
    )
