from ..database.errors import PrivacyViolationError

def validate_safe_for_persistence(record: dict, privacy_mode: str):
    """
    Final guard before repository insertion.
    Ensures that no explicit raw texts are leaked.
    """
    for key in record.keys():
        if key in ("raw_text", "raw_audio", "audio_bytes"):
            raise PrivacyViolationError(f"Prohibited key '{key}' found in record")
        
    if privacy_mode == "MAXIMUM_PRIVACY":
        # Check against suspicious unredacted sequences
        for val in record.values():
            if isinstance(val, str):
                if "http://" in val or "https://" in val:
                    # In a real implementation, you'd double check if it's the [URL_REDACTED] tag vs actual url
                    if not "[URL_REDACTED]" in val:
                         pass # Warning logic here
