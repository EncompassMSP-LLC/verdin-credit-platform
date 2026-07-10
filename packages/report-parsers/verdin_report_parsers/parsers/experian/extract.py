"""Field extraction for Experian 2026 consumer credit report layouts."""

from __future__ import annotations

import re

from verdin_report_parsers.helpers import mask_account_number, mask_ssn, parse_balance
from verdin_report_parsers.models import (
    Collection,
    ConsumerInfo,
    Inquiry,
    PublicRecord,
    ReportSummary,
    TradelineAccount,
)

_FIELD_CONFIDENCE = 0.92
_CONSUMER_CONFIDENCE = 0.95

_NAME_RE = re.compile(r"^Name:\s*(.+)$", re.I | re.M)
_DOB_RE = re.compile(r"^Date of Birth:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_SSN_RE = re.compile(r"^SSN:\s*(\d{3}-\d{2}-\d{4})$", re.I | re.M)

_ACCOUNT_BLOCK_RE = re.compile(
    r"^Account\s+(\d+)\s*\n(.*?)(?=^Account\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_CREDITOR_RE = re.compile(r"^Creditor:\s*(.+)$", re.I | re.M)
_ACCOUNT_NUMBER_RE = re.compile(r"^Account Number:\s*(.+)$", re.I | re.M)
_ACCOUNT_TYPE_RE = re.compile(r"^Account Type:\s*(.+)$", re.I | re.M)
_BALANCE_RE = re.compile(r"^Balance:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_CREDIT_LIMIT_RE = re.compile(r"^Credit Limit:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_PAYMENT_STATUS_RE = re.compile(r"^Payment Status:\s*(.+)$", re.I | re.M)
_OPEN_DATE_RE = re.compile(r"^Date Opened:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_REPORTED_DATE_RE = re.compile(r"^Date Reported:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)

_INQUIRY_BLOCK_RE = re.compile(
    r"^Inquiry\s+(\d+)\s*\n(.*?)(?=^Inquiry\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_INQUIRED_BY_RE = re.compile(r"^Inquired By:\s*(.+)$", re.I | re.M)
_INQUIRY_DATE_RE = re.compile(r"^Inquiry Date:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_INQUIRY_TYPE_RE = re.compile(r"^Inquiry Type:\s*(.+)$", re.I | re.M)

_PUBLIC_RECORD_BLOCK_RE = re.compile(
    r"^Record\s+(\d+)\s*\n(.*?)(?=^Record\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_RECORD_TYPE_RE = re.compile(r"^Record Type:\s*(.+)$", re.I | re.M)
_FILING_DATE_RE = re.compile(r"^Filing Date:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_RECORD_STATUS_RE = re.compile(r"^Status:\s*(.+)$", re.I | re.M)
_RECORD_AMOUNT_RE = re.compile(r"^Amount:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)

_COLLECTION_BLOCK_RE = re.compile(
    r"^Collection\s+(\d+)\s*\n(.*?)(?=^Collection\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_AGENCY_RE = re.compile(r"^Collection Agency:\s*(.+)$", re.I | re.M)
_ORIGINAL_CREDITOR_RE = re.compile(r"^Original Creditor:\s*(.+)$", re.I | re.M)
_COLLECTION_BALANCE_RE = re.compile(r"^Balance:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_COLLECTION_STATUS_RE = re.compile(r"^Status:\s*(.+)$", re.I | re.M)

_REPORT_DATE_RE = re.compile(r"^Report Date:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_DATE_GENERATED_RE = re.compile(
    r"Date Generated\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})",
    re.I,
)
_PREPARED_FOR_RE = re.compile(r"Prepared For\s*\n([A-Z][A-Z .'-]{2,80})", re.I | re.M)
_YEAR_OF_BIRTH_RE = re.compile(r"Year of Birth\s*\n(\d{4})", re.I | re.M)
_ACR_ACCOUNT_INFO_RE = re.compile(
    r"Account Info\s*\n"
    r"Account Name\s+(.+?)\s*\n"
    r"Account Number\s+(.+?)\s*\n"
    r"Account Type\s+(.+?)\s*\n"
    r"(?:.*?\n)*?"
    r"Date Opened\s+(\d{1,2}/\d{1,2}/\d{4})\s*\n"
    r"Status\s+(.+?)\s*\n"
    r"(?:.*?\n)*?"
    r"Balance\s+\$?([\d,]+)",
    re.I | re.S,
)
_ACR_INQUIRY_RE = re.compile(
    r"^([A-Z0-9][A-Z0-9 &.'/-]{1,60})\s*\nInquired on\s+(\d{1,2}/\d{1,2}/\d{4})",
    re.I | re.M,
)


def _first(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def _normalize_long_date(raw: str) -> str:
    from datetime import datetime

    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%m/%d/%Y")
        except ValueError:
            continue
    return raw.strip()


def extract_consumer(section_text: str, full_text: str) -> tuple[ConsumerInfo | None, dict[str, float]]:
    name = _first(_NAME_RE, section_text) or _first(_PREPARED_FOR_RE, full_text)
    dob = _first(_DOB_RE, section_text)
    if not dob:
        year = _first(_YEAR_OF_BIRTH_RE, section_text) or _first(_YEAR_OF_BIRTH_RE, full_text)
        if year:
            dob = f"01/01/{year}"
    ssn_raw = _first(_SSN_RE, section_text)
    ssn_masked = mask_ssn(ssn_raw) if ssn_raw else mask_ssn(full_text)

    field_confidence: dict[str, float] = {}
    if name:
        field_confidence["consumer.name"] = _CONSUMER_CONFIDENCE
    if dob:
        field_confidence["consumer.date_of_birth"] = _CONSUMER_CONFIDENCE
    if ssn_masked:
        field_confidence["consumer.ssn_masked"] = _CONSUMER_CONFIDENCE

    if not (name or dob or ssn_masked):
        return None, field_confidence

    consumer_confidences = [
        field_confidence[key]
        for key in ("consumer.name", "consumer.date_of_birth", "consumer.ssn_masked")
        if key in field_confidence
    ]
    return (
        ConsumerInfo(
            name=name,
            date_of_birth=dob,
            ssn_masked=ssn_masked,
            confidence=max(consumer_confidences) if consumer_confidences else 0.0,
        ),
        field_confidence,
    )


def _extract_acr_accounts(
    text: str,
    *,
    start_index: int,
    field_confidence: dict[str, float],
) -> tuple[list[TradelineAccount], int]:
    accounts: list[TradelineAccount] = []
    index = start_index

    for match in _ACR_ACCOUNT_INFO_RE.finditer(text):
        creditor = match.group(1).strip()
        account_number_raw = match.group(2).strip()
        account_type = match.group(3).strip()
        open_date = match.group(4).strip()
        payment_status = re.sub(r"\s+", " ", match.group(5).strip())
        balance = parse_balance(match.group(6))

        account_masked = mask_account_number(account_number_raw)
        prefix = f"accounts[{index}]"
        if creditor:
            field_confidence[f"{prefix}.creditor_name"] = _FIELD_CONFIDENCE
        if account_masked:
            field_confidence[f"{prefix}.account_number_masked"] = _FIELD_CONFIDENCE
        if account_type:
            field_confidence[f"{prefix}.account_type"] = _FIELD_CONFIDENCE
        if balance is not None:
            field_confidence[f"{prefix}.balance"] = _FIELD_CONFIDENCE
        if payment_status:
            field_confidence[f"{prefix}.payment_status"] = _FIELD_CONFIDENCE
        if open_date:
            field_confidence[f"{prefix}.open_date"] = _FIELD_CONFIDENCE

        account_scores = [field_confidence[key] for key in field_confidence if key.startswith(prefix)]
        accounts.append(
            TradelineAccount(
                creditor_name=creditor,
                account_number_masked=account_masked,
                account_type=account_type,
                balance=balance,
                credit_limit=None,
                payment_status=payment_status,
                open_date=open_date,
                date_reported=None,
                bureau="experian",
                confidence=max(account_scores) if account_scores else 0.0,
            )
        )
        index += 1

    return accounts, index


def extract_accounts(
    section_text: str,
    *,
    full_text: str | None = None,
) -> tuple[tuple[TradelineAccount, ...], dict[str, float]]:
    accounts: list[TradelineAccount] = []
    field_confidence: dict[str, float] = {}

    for index, match in enumerate(_ACCOUNT_BLOCK_RE.finditer(section_text)):
        block = match.group(2)
        creditor = _first(_CREDITOR_RE, block)
        account_number_raw = _first(_ACCOUNT_NUMBER_RE, block)
        account_type = _first(_ACCOUNT_TYPE_RE, block)
        balance = parse_balance(_first(_BALANCE_RE, block))
        credit_limit = parse_balance(_first(_CREDIT_LIMIT_RE, block))
        payment_status = _first(_PAYMENT_STATUS_RE, block)
        open_date = _first(_OPEN_DATE_RE, block)
        date_reported = _first(_REPORTED_DATE_RE, block)
        account_masked = mask_account_number(account_number_raw) if account_number_raw else None

        prefix = f"accounts[{index}]"
        if creditor:
            field_confidence[f"{prefix}.creditor_name"] = _FIELD_CONFIDENCE
        if account_masked:
            field_confidence[f"{prefix}.account_number_masked"] = _FIELD_CONFIDENCE
        if account_type:
            field_confidence[f"{prefix}.account_type"] = _FIELD_CONFIDENCE
        if balance is not None:
            field_confidence[f"{prefix}.balance"] = _FIELD_CONFIDENCE
        if credit_limit is not None:
            field_confidence[f"{prefix}.credit_limit"] = _FIELD_CONFIDENCE
        if payment_status:
            field_confidence[f"{prefix}.payment_status"] = _FIELD_CONFIDENCE
        if open_date:
            field_confidence[f"{prefix}.open_date"] = _FIELD_CONFIDENCE
        if date_reported:
            field_confidence[f"{prefix}.date_reported"] = _FIELD_CONFIDENCE

        account_field_scores = [
            field_confidence[key] for key in field_confidence if key.startswith(prefix)
        ]
        accounts.append(
            TradelineAccount(
                creditor_name=creditor,
                account_number_masked=account_masked,
                account_type=account_type,
                balance=balance,
                credit_limit=credit_limit,
                payment_status=payment_status,
                open_date=open_date,
                date_reported=date_reported,
                bureau="experian",
                confidence=max(account_field_scores) if account_field_scores else 0.0,
            )
        )

    if not accounts:
        acr_source = section_text or full_text or ""
        acr_accounts, _ = _extract_acr_accounts(acr_source, start_index=0, field_confidence=field_confidence)
        accounts.extend(acr_accounts)

    return tuple(accounts), field_confidence


def extract_inquiries(section_text: str) -> tuple[tuple[Inquiry, ...], dict[str, float]]:
    inquiries: list[Inquiry] = []
    field_confidence: dict[str, float] = {}

    for index, match in enumerate(_INQUIRY_BLOCK_RE.finditer(section_text)):
        block = match.group(2)
        creditor = _first(_INQUIRED_BY_RE, block)
        inquiry_date = _first(_INQUIRY_DATE_RE, block)
        inquiry_type = _first(_INQUIRY_TYPE_RE, block)
        prefix = f"inquiries[{index}]"

        if creditor:
            field_confidence[f"{prefix}.creditor_name"] = _FIELD_CONFIDENCE
        if inquiry_date:
            field_confidence[f"{prefix}.inquiry_date"] = _FIELD_CONFIDENCE
        if inquiry_type:
            field_confidence[f"{prefix}.inquiry_type"] = _FIELD_CONFIDENCE

        inquiry_scores = [field_confidence[key] for key in field_confidence if key.startswith(prefix)]
        inquiries.append(
            Inquiry(
                creditor_name=creditor,
                inquiry_date=inquiry_date,
                inquiry_type=inquiry_type,
                confidence=max(inquiry_scores) if inquiry_scores else 0.0,
            )
        )

    if not inquiries:
        for index, match in enumerate(_ACR_INQUIRY_RE.finditer(section_text)):
            creditor = match.group(1).strip()
            inquiry_date = match.group(2).strip()
            prefix = f"inquiries[{index}]"
            field_confidence[f"{prefix}.creditor_name"] = _FIELD_CONFIDENCE
            field_confidence[f"{prefix}.inquiry_date"] = _FIELD_CONFIDENCE
            inquiries.append(
                Inquiry(
                    creditor_name=creditor,
                    inquiry_date=inquiry_date,
                    inquiry_type="Hard",
                    confidence=_FIELD_CONFIDENCE,
                )
            )

    return tuple(inquiries), field_confidence


def extract_public_records(section_text: str) -> tuple[tuple[PublicRecord, ...], dict[str, float]]:
    records: list[PublicRecord] = []
    field_confidence: dict[str, float] = {}

    for index, match in enumerate(_PUBLIC_RECORD_BLOCK_RE.finditer(section_text)):
        block = match.group(2)
        record_type = _first(_RECORD_TYPE_RE, block)
        filing_date = _first(_FILING_DATE_RE, block)
        status = _first(_RECORD_STATUS_RE, block)
        amount = parse_balance(_first(_RECORD_AMOUNT_RE, block))
        prefix = f"public_records[{index}]"

        if record_type:
            field_confidence[f"{prefix}.record_type"] = _FIELD_CONFIDENCE
        if filing_date:
            field_confidence[f"{prefix}.filing_date"] = _FIELD_CONFIDENCE
        if status:
            field_confidence[f"{prefix}.status"] = _FIELD_CONFIDENCE
        if amount is not None:
            field_confidence[f"{prefix}.amount"] = _FIELD_CONFIDENCE

        record_scores = [field_confidence[key] for key in field_confidence if key.startswith(prefix)]
        records.append(
            PublicRecord(
                record_type=record_type,
                filing_date=filing_date,
                status=status,
                amount=amount,
                confidence=max(record_scores) if record_scores else 0.0,
            )
        )

    return tuple(records), field_confidence


def extract_collections(section_text: str) -> tuple[tuple[Collection, ...], dict[str, float]]:
    collections: list[Collection] = []
    field_confidence: dict[str, float] = {}

    for index, match in enumerate(_COLLECTION_BLOCK_RE.finditer(section_text)):
        block = match.group(2)
        agency = _first(_AGENCY_RE, block)
        original_creditor = _first(_ORIGINAL_CREDITOR_RE, block)
        balance = parse_balance(_first(_COLLECTION_BALANCE_RE, block))
        status = _first(_COLLECTION_STATUS_RE, block)
        prefix = f"collections[{index}]"

        if agency:
            field_confidence[f"{prefix}.agency_name"] = _FIELD_CONFIDENCE
        if original_creditor:
            field_confidence[f"{prefix}.original_creditor"] = _FIELD_CONFIDENCE
        if balance is not None:
            field_confidence[f"{prefix}.balance"] = _FIELD_CONFIDENCE
        if status:
            field_confidence[f"{prefix}.status"] = _FIELD_CONFIDENCE

        collection_scores = [
            field_confidence[key] for key in field_confidence if key.startswith(prefix)
        ]
        collections.append(
            Collection(
                agency_name=agency,
                original_creditor=original_creditor,
                balance=balance,
                status=status,
                confidence=max(collection_scores) if collection_scores else 0.0,
            )
        )

    return tuple(collections), field_confidence


def build_summary(
    accounts: tuple[TradelineAccount, ...],
    inquiries: tuple[Inquiry, ...],
    public_records: tuple[PublicRecord, ...],
    collections: tuple[Collection, ...],
    field_confidence: dict[str, float],
) -> ReportSummary:
    balances = [account.balance for account in accounts if account.balance is not None]
    total_balance = round(sum(balances), 2) if balances else None
    summary_confidence = max(field_confidence.values()) if field_confidence else 0.0

    return ReportSummary(
        total_accounts=len(accounts),
        total_inquiries=len(inquiries),
        total_public_records=len(public_records),
        total_collections=len(collections),
        total_balance=total_balance,
        confidence=summary_confidence,
    )


def extract_report_date(full_text: str) -> tuple[str | None, dict[str, float]]:
    report_date = _first(_REPORT_DATE_RE, full_text)
    if not report_date:
        generated = _first(_DATE_GENERATED_RE, full_text)
        if generated:
            report_date = _normalize_long_date(generated)
    if not report_date:
        return None, {}
    return report_date, {"report.report_date": _FIELD_CONFIDENCE}
