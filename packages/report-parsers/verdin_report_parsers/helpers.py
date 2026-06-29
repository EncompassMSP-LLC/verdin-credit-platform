"""Shared extraction helpers for partial report parsing."""

import re

from verdin_report_parsers.constants import Bureau

_BUREAU_PATTERNS: dict[Bureau, re.Pattern[str]] = {
    Bureau.EXPERIAN: re.compile(r"\bexperian\b", re.I),
    Bureau.EQUIFAX: re.compile(r"\bequifax\b", re.I),
    Bureau.TRANSUNION: re.compile(r"\btrans\s*union\b|\btransunion\b", re.I),
    Bureau.INNOVIS: re.compile(r"\binnovis\b", re.I),
}

_CONSUMER_RE = re.compile(
    r"(?:consumer name|name of consumer|account holder)[:\s]*([A-Za-z ,.'-]{3,80})",
    re.I,
)
_DOB_RE = re.compile(
    r"(?:date of birth|dob)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    re.I,
)
_SSN_RE = re.compile(r"\b(\d{3})-(\d{2})-(\d{4})\b")
_ACCOUNT_RE = re.compile(
    r"(?:account(?:\s*#| number)?|acct\.?)[:\s#]*([xX*#\d\-]{4,})",
    re.I,
)
_BALANCE_RE = re.compile(r"(?:balance|amount due|past due)[:\s]*\$?([\d,]+\.?\d*)", re.I)
_CREDITOR_RE = re.compile(
    r"(?:creditor|furnisher|lender)[:\s]*([A-Za-z0-9 &.'-]{3,80})",
    re.I,
)
_COLLECTION_RE = re.compile(
    r"(?:collection agency|collector)[:\s]*([A-Za-z0-9 &.'-]{3,80})",
    re.I,
)
_REPORT_DATE_RE = re.compile(
    r"(?:report date|date reported|as of)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    re.I,
)
_OPEN_DATE_RE = re.compile(
    r"(?:date opened|opened)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    re.I,
)
_PAYMENT_STATUS_RE = re.compile(
    r"(?:payment status|account status|status)[:\s]*([A-Za-z0-9 /_-]{3,40})",
    re.I,
)
_INQUIRY_RE = re.compile(
    r"(?:inquiry|inquired by)[:\s]*([A-Za-z0-9 &.'-]{3,80})",
    re.I,
)
_ADDRESS_RE = re.compile(
    r"(?:address)[:\s]*([0-9]{1,6}\s+[A-Za-z0-9 .,'-]{5,80})",
    re.I,
)


def detect_bureau(text: str) -> Bureau:
    for bureau, pattern in _BUREAU_PATTERNS.items():
        if pattern.search(text):
            return bureau
    return Bureau.UNKNOWN


def first_match(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def mask_account_number(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if len(digits) >= 4:
        return f"****{digits[-4:]}"
    return "****"


def mask_ssn(raw: str) -> str | None:
    match = _SSN_RE.search(raw)
    if not match:
        return None
    return f"***-**-{match.group(3)}"


def parse_balance(raw: str | None) -> float | None:
    if not raw:
        return None
    try:
        return float(raw.replace(",", ""))
    except ValueError:
        return None


def extract_consumer_name(text: str) -> tuple[str | None, float]:
    value = first_match(_CONSUMER_RE, text)
    return value, 0.55 if value else 0.0


def extract_dob(text: str) -> tuple[str | None, float]:
    value = first_match(_DOB_RE, text)
    return value, 0.5 if value else 0.0


def extract_ssn_masked(text: str) -> tuple[str | None, float]:
    value = mask_ssn(text)
    return value, 0.45 if value else 0.0


def extract_creditor(text: str) -> tuple[str | None, float]:
    value = first_match(_CREDITOR_RE, text)
    return value, 0.5 if value else 0.0


def extract_account_number_masked(text: str) -> tuple[str | None, float]:
    raw = first_match(_ACCOUNT_RE, text)
    if not raw:
        return None, 0.0
    return mask_account_number(raw), 0.5


def extract_balance(text: str) -> tuple[float | None, float]:
    raw = first_match(_BALANCE_RE, text)
    value = parse_balance(raw)
    return value, 0.45 if value is not None else 0.0


def extract_payment_status(text: str) -> tuple[str | None, float]:
    value = first_match(_PAYMENT_STATUS_RE, text)
    return value, 0.4 if value else 0.0


def extract_open_date(text: str) -> tuple[str | None, float]:
    value = first_match(_OPEN_DATE_RE, text)
    return value, 0.4 if value else 0.0


def extract_report_date(text: str) -> tuple[str | None, float]:
    value = first_match(_REPORT_DATE_RE, text)
    return value, 0.4 if value else 0.0


def extract_collection_agency(text: str) -> tuple[str | None, float]:
    value = first_match(_COLLECTION_RE, text)
    return value, 0.45 if value else 0.0


def extract_inquiry_creditor(text: str) -> tuple[str | None, float]:
    value = first_match(_INQUIRY_RE, text)
    return value, 0.35 if value else 0.0


def extract_address(text: str) -> tuple[str | None, float]:
    value = first_match(_ADDRESS_RE, text)
    return value, 0.35 if value else 0.0
