"""Rule-based metadata field extraction."""

import re
from datetime import datetime

from verdin_document_metadata.base import ExtractedMetadata, ExtractionContext

_BUREAU_PATTERNS = {
    "equifax": re.compile(r"\bequifax\b", re.I),
    "experian": re.compile(r"\bexperian\b", re.I),
    "transunion": re.compile(r"\btrans\s*union\b|\btransunion\b", re.I),
    "innovis": re.compile(r"\binnovis\b", re.I),
}

_PHONE_RE = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
_SSN_RE = re.compile(r"\b(\d{3})-(\d{2})-(\d{4})\b")
_BALANCE_RE = re.compile(r"(?:balance|amount due|past due)[:\s]*\$?([\d,]+\.?\d*)", re.I)
_ACCOUNT_RE = re.compile(
    r"(?:account(?:\s*#| number)?|acct\.?)[:\s#]*([xX*#\d\-]{4,})",
    re.I,
)
_DATE_RE = re.compile(
    r"(?:report date|date reported|as of)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    re.I,
)
_OPEN_DATE_RE = re.compile(
    r"(?:date opened|opened)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    re.I,
)
_CONSUMER_RE = re.compile(
    r"(?:consumer name|name of consumer|account holder)[:\s]*([A-Za-z ,.'-]{3,80})",
    re.I,
)
_CREDITOR_RE = re.compile(
    r"(?:creditor|furnisher|lender)[:\s]*([A-Za-z0-9 &.'-]{3,80})",
    re.I,
)
_COLLECTION_RE = re.compile(
    r"(?:collection agency|collector)[:\s]*([A-Za-z0-9 &.'-]{3,80})",
    re.I,
)
_ADDRESS_RE = re.compile(
    r"(?:address)[:\s]*([0-9]{1,6}\s+[A-Za-z0-9 .,'-]{5,80})",
    re.I,
)
_PAYMENT_STATUS_RE = re.compile(
    r"(?:payment status|account status|status)[:\s]*([A-Za-z0-9 /_-]{3,40})",
    re.I,
)


def _first_match(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def _mask_account_number(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if len(digits) >= 4:
        return f"****{digits[-4:]}"
    return "****"


def _mask_ssn(raw: str) -> str:
    match = _SSN_RE.search(raw)
    if not match:
        return raw
    return f"***-**-{match.group(3)}"


def _parse_balance(raw: str | None) -> float | None:
    if not raw:
        return None
    try:
        return float(raw.replace(",", ""))
    except ValueError:
        return None


def _normalize_date(raw: str | None) -> str | None:
    if not raw:
        return None
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    return raw


def extract_metadata(context: ExtractionContext) -> ExtractedMetadata:
    parts = [context.title, context.file_name]
    if context.ocr_text:
        parts.append(context.ocr_text)
    text = "\n".join(parts)
    if not text.strip():
        return ExtractedMetadata(confidence_score=0.0)

    field_confidence: dict[str, float] = {}
    consumer_name = _first_match(_CONSUMER_RE, text)
    if consumer_name:
        field_confidence["consumer_name"] = 0.75

    bureau = None
    for name, pattern in _BUREAU_PATTERNS.items():
        if pattern.search(text):
            bureau = name
            field_confidence["bureau"] = 0.85
            break

    creditor = _first_match(_CREDITOR_RE, text)
    if creditor:
        field_confidence["creditor"] = 0.7

    collection_agency = _first_match(_COLLECTION_RE, text)
    if collection_agency:
        field_confidence["collection_agency"] = 0.7

    account_raw = _first_match(_ACCOUNT_RE, text)
    account_number_masked = _mask_account_number(account_raw) if account_raw else None
    if account_number_masked:
        field_confidence["account_number_masked"] = 0.8

    report_date = _normalize_date(_first_match(_DATE_RE, text))
    if report_date:
        field_confidence["report_date"] = 0.65

    open_date = _normalize_date(_first_match(_OPEN_DATE_RE, text))
    if open_date:
        field_confidence["open_date"] = 0.65

    balance = _parse_balance(_first_match(_BALANCE_RE, text))
    if balance is not None:
        field_confidence["balance"] = 0.6

    payment_status = _first_match(_PAYMENT_STATUS_RE, text)
    if payment_status:
        field_confidence["payment_status"] = 0.55

    addresses = tuple(
        match.group(1).strip() for match in _ADDRESS_RE.finditer(text) if match.group(1)
    )[:3]
    if addresses:
        field_confidence["addresses"] = 0.6

    phone_numbers = tuple(dict.fromkeys(_PHONE_RE.findall(text)))[:5]
    if phone_numbers:
        field_confidence["phone_numbers"] = 0.7

    ssn_match = _SSN_RE.search(text)
    ssn_masked = _mask_ssn(ssn_match.group(0)) if ssn_match else None
    if ssn_masked:
        field_confidence["ssn_masked"] = 0.9

    confidence_score = (
        sum(field_confidence.values()) / len(field_confidence) if field_confidence else 0.0
    )

    return ExtractedMetadata(
        consumer_name=consumer_name,
        bureau=bureau,
        creditor=creditor,
        collection_agency=collection_agency,
        account_number_masked=account_number_masked,
        report_date=report_date,
        open_date=open_date,
        balance=balance,
        payment_status=payment_status,
        addresses=addresses,
        phone_numbers=phone_numbers,
        ssn_masked=ssn_masked,
        confidence_score=round(confidence_score, 4),
        field_confidence=field_confidence,
    )
