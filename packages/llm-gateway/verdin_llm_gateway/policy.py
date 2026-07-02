"""PII scrubbing helpers for LLM prompts."""

import re
from typing import Any

PII_FIELD_NAMES: frozenset[str] = frozenset(
    {
        "ssn",
        "social_security_number",
        "date_of_birth",
        "dob",
        "account_number",
        "full_account_number",
        "client_email",
        "email",
        "phone",
        "address",
        "street",
        "postal_code",
        "zip",
    }
)

_SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_PATTERN = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b")


def redact_pii(text: str) -> str:
    """Best-effort redaction of common PII patterns in free text."""
    redacted = _SSN_PATTERN.sub("[REDACTED_SSN]", text)
    redacted = _EMAIL_PATTERN.sub("[REDACTED_EMAIL]", redacted)
    return _PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)


def scrub_payload(value: Any) -> Any:
    """Recursively remove known PII keys and redact string values."""
    if isinstance(value, dict):
        scrubbed: dict[Any, Any] = {}
        for key, item in value.items():
            if str(key).lower() in PII_FIELD_NAMES:
                scrubbed[key] = "[REDACTED]"
                continue
            scrubbed[key] = scrub_payload(item)
        return scrubbed
    if isinstance(value, list):
        return [scrub_payload(item) for item in value]
    if isinstance(value, str):
        return redact_pii(value)
    return value
