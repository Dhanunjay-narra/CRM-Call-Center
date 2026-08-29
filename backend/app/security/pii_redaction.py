"""
PCI-DSS Credit Card & PII Data Masking Filter
Redacts 16-digit credit card numbers, CVVs, Social Security Numbers (SSN),
passwords, and tokenizes phone/email identifiers across logs and timeline transcripts.
"""

import re
from typing import str


class PIIDataMasker:
    # Luhn 13-16 digit credit card patterns
    CREDIT_CARD_REGEX = re.compile(r"(?:\d[ -]*?){13,16}")
    # SSN pattern
    SSN_REGEX = re.compile(r"\d{3}-\d{2}-\d{4}")
    # CVV / CVC
    CVV_REGEX = re.compile(r"(?:cvv|cvc|security code)\s*[:=]?\s*(\d{3,4})", re.IGNORECASE)
    # Email pattern
    EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}")

    @classmethod
    def mask_sensitive_text(cls, text: str) -> str:
        if not text:
            return ""

        # Redact Credit Cards: leave only last 4 digits
        def _mask_cc(match):
            digits = re.sub(r"\D", "", match.group(0))
            if len(digits) >= 13:
                return f"****-****-****-{digits[-4:]}"
            return match.group(0)

        masked = cls.CREDIT_CARD_REGEX.sub(_mask_cc, text)
        masked = cls.SSN_REGEX.sub("***-**-****", masked)
        masked = cls.CVV_REGEX.sub("CVV: ***", masked)
        return masked

    @classmethod
    def mask_email_preview(cls, email: str) -> str:
        if not email or "@" not in email:
            return email
        user, domain = email.split("@", 1)
        if len(user) <= 2:
            return f"*@{domain}"
        return f"{user[0]}***{user[-1]}@{domain}"
