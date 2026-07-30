import re
from typing import Optional

def redact_sensitive_text(raw_text: str) -> str:
    """
    Redacts sensitive content in the following order:
    1. URLs/Emails
    2. UPI IDs
    3. PAN
    4. Aadhaar
    5. Card numbers
    6. OTP/PIN
    """
    if not raw_text:
        return raw_text
        
    text = raw_text
    # 1. Email/UPI basic redaction
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL_UPI_REDACTED]', text)
    # 2. URLs
    text = re.sub(r'https?://[^\s]+', '[URL_REDACTED]', text)
    # 3. PAN (basic Indian PAN format: 5 letters, 4 numbers, 1 letter)
    text = re.sub(r'\b[A-Z]{5}\d{4}[A-Z]\b', '[PAN_REDACTED]', text)
    # 4. Aadhaar (12 digits space separated)
    text = re.sub(r'\b\d{4}\s\d{4}\s\d{4}\b', '[AADHAAR_REDACTED]', text)
    # 5. OTP (4-6 digits)
    text = re.sub(r'\b\d{4,6}\b', '[OTP_PIN_REDACTED]', text)
    # 6. Large numbers (account, cards)
    text = re.sub(r'\b\d{10,16}\b', '[ACCOUNT_REDACTED]', text)
    
    return text
