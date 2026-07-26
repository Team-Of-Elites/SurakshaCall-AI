import re

class Redactor:
    """
    Handles the removal of Personally Identifiable Information (PII) 
    and sensitive financial data from transcripts before they are persisted.
    """
    
    # Pre-compile regex patterns for performance
    PATTERNS = {
        # Matches typical 4 to 8 digit OTPs/PINs (avoids matching short normal numbers by word boundaries)
        "OTP": re.compile(r'\b\d{4,8}\b'),
        
        # Indian Aadhaar (12 digits, optional spaces)
        "AADHAAR": re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b'),
        
        # Indian PAN Card (5 letters, 4 numbers, 1 letter)
        "PAN": re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', re.IGNORECASE),
        
        # Standard Credit/Debit Card (12-19 digits, optional dashes or spaces)
        "CARD": re.compile(r'\b(?:\d[ -]*?){13,19}\b'),
        
        # UPI ID (username@bank)
        "UPI": re.compile(r'\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b'),
        
        # Standard Emails
        "EMAIL": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'),
        
        # Phone Numbers (10 digits, optional country code)
        "PHONE": re.compile(r'\b(?:\+?91[\-\s]?)?[7896]\d{9}\b'),
        
        # URLs
        "URL": re.compile(r'\b(?:http|https)://[^\s]+\b|www\.[^\s]+\b')
    }

    @classmethod
    def redact_transcript(cls, text: str) -> str:
        """
        Takes raw transcribed text and replaces sensitive patterns with safe placeholders.
        The order of redaction matters (e.g., redact Aadhaar before generic OTPs).
        """
        if not text:
            return text
            
        redacted_text = text
        
        # Order of execution is important to prevent smaller regexes (like OTP) 
        # from breaking apart larger regexes (like Aadhaar or Cards).
        ordered_keys = ["URL", "EMAIL", "UPI", "PAN", "CARD", "AADHAAR", "PHONE", "OTP"]
        
        for key in ordered_keys:
            pattern = cls.PATTERNS[key]
            placeholder = f"[{key}_REDACTED]"
            redacted_text = pattern.sub(placeholder, redacted_text)
            
        return redacted_text
