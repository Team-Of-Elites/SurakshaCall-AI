from enum import Enum
from typing import Dict, Any

class RetentionMode(Enum):
    MAXIMUM_PRIVACY = "MAXIMUM_PRIVACY"
    EVALUATION = "EVALUATION"

class RetentionManager:
    """
    Manages the data retention policy.
    In MAXIMUM_PRIVACY mode, raw audio, unredacted transcripts, 
    and even redacted transcripts are NOT saved to the database.
    In EVALUATION mode, redacted transcripts and evidence events ARE saved for later analysis.
    """
    
    def __init__(self, mode: RetentionMode = RetentionMode.MAXIMUM_PRIVACY):
        self.current_mode = mode
        
    def set_mode(self, mode: RetentionMode):
        self.current_mode = mode
        
    def get_mode(self) -> RetentionMode:
        return self.current_mode
        
    def should_save_transcript(self) -> bool:
        """Returns True if redacted transcripts should be saved to the database."""
        return self.current_mode == RetentionMode.EVALUATION

    def should_save_audio(self) -> bool:
        """
        By default, raw audio is NEVER saved, regardless of the evaluation mode.
        It strictly lives in the in-memory ring buffer.
        """
        return False
        
# Global instance for the backend to use
retention_manager = RetentionManager()