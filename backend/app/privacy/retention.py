from typing import Optional

class RetentionPolicy:
    def should_persist_utterance(self, privacy_mode: str) -> bool:
        if privacy_mode == "MAXIMUM_PRIVACY":
            return False
        return True # EVALUATION mode or other explicit mode

    def should_persist_evidence(self, privacy_mode: str) -> bool:
        return True

    def should_persist_risk(self, privacy_mode: str) -> bool:
        return True

    def should_persist_pattern_match(self, privacy_mode: str) -> bool:
        return True

    def deletion_due_at(self, privacy_mode: str, started_at_utc: str) -> Optional[str]:
        # Typically calculate an expiration time depending on policy.
        # Returning None implies immediate/session-bound lifecycle
        return None