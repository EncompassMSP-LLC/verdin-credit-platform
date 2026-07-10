"""Field extraction for Equifax 2026 consumer credit report layouts."""

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

_FIELD_CONFIDENCE = 0.91
_CONSUMER_CONFIDENCE = 0.94

_CONSUMER_RE = re.compile(r"^Consumer:\s*(.+)$", re.I | re.M)
_DOB_RE = re.compile(r"^DOB:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_SSN_RE = re.compile(r"^Social Security Number:\s*(\d{3}-\d{2}-\d{4})$", re.I | re.M)

_TRADELINE_BLOCK_RE = re.compile(
    r"^Tradeline\s+(\d+)\s*\n(.*?)(?=^Tradeline\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_FURNISHER_RE = re.compile(r"^Furnisher:\s*(.+)$", re.I | re.M)
_ACCOUNT_IDENTIFIER_RE = re.compile(r"^Account Identifier:\s*(.+)$", re.I | re.M)
_PORTFOLIO_TYPE_RE = re.compile(r"^Portfolio Type:\s*(.+)$", re.I | re.M)
_CURRENT_BALANCE_RE = re.compile(r"^Current Balance:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_HIGH_CREDIT_RE = re.compile(r"^High Credit:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_ACCOUNT_STATUS_RE = re.compile(r"^Account Status:\s*(.+)$", re.I | re.M)
_DATE_OPENED_RE = re.compile(r"^Opened:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_LAST_REPORTED_RE = re.compile(r"^Last Reported:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)

_INQUIRY_BLOCK_RE = re.compile(
    r"^Inquiry\s+(\d+)\s*\n(.*?)(?=^Inquiry\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_REQUESTED_BY_RE = re.compile(r"^Requested By:\s*(.+)$", re.I | re.M)
_DATE_OF_INQUIRY_RE = re.compile(r"^Date of Inquiry:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_PURPOSE_RE = re.compile(r"^Purpose:\s*(.+)$", re.I | re.M)

_PUBLIC_RECORD_BLOCK_RE = re.compile(
    r"^Public Record\s+(\d+)\s*\n(.*?)(?=^Public Record\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_TYPE_RE = re.compile(r"^Type:\s*(.+)$", re.I | re.M)
_FILED_RE = re.compile(r"^Filed:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_STATUS_RE = re.compile(r"^Status:\s*(.+)$", re.I | re.M)
_AMOUNT_RE = re.compile(r"^Amount:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)

_COLLECTION_BLOCK_RE = re.compile(
    r"^Collection Account\s+(\d+)\s*\n(.*?)(?=^Collection Account\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_AGENCY_RE = re.compile(r"^Agency:\s*(.+)$", re.I | re.M)
_ORIGINAL_CREDITOR_RE = re.compile(r"^Original Creditor:\s*(.+)$", re.I | re.M)
_COLLECTION_BALANCE_RE = re.compile(r"^Current Balance:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_COLLECTION_STATUS_RE = re.compile(r"^Status:\s*(.+)$", re.I | re.M)

_REPORT_DATE_RE = re.compile(r"^Report Date:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_ACR_DATE_RE = re.compile(r"^Date:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})", re.I | re.M)
_PREPARED_FOR_RE = re.compile(r"Prepared for:\s*\n([A-Z][A-Z .'-]{2,80})", re.I | re.M)
_ACR_DOB_RE = re.compile(r"Date of Birth:\s*(\d{1,2}/\d{1,2}/\d{4})", re.I)
_ACR_SSN_RE = re.compile(r"Social Security Number:\s*(XXX-XX-\d{4})", re.I)
_ACR_ACCOUNT_RE = re.compile(
    r"(?:^|\n)[ \t]{8,}([A-Za-z0-9][A-Za-z0-9 &.'-]{2,80}?)\s+-\s+(?:Open|Closed|Paid|Transferred)\s*\n"
    r".*?Date Reported:\s*(\d{1,2}/\d{1,2}/\d{4}).*?Balance:\s*\$?([\d,]+)"
    r".*?Account Number:\s*([^\|\n]+)"
    r".*?Loan/Account Type:\s*([^|\n]+)"
    r".*?Date Opened:\s*(\d{1,2}/\d{1,2}/\d{4})",
    re.I | re.S,
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
    consumer_name = (
        _first(_CONSUMER_RE, section_text)
        or _first(_PREPARED_FOR_RE, full_text)
        or _first(_PREPARED_FOR_RE, section_text)
    )
    dob = _first(_DOB_RE, section_text) or _first(_ACR_DOB_RE, section_text) or _first(_ACR_DOB_RE, full_text)
    ssn_raw = _first(_SSN_RE, section_text)
    ssn_masked = mask_ssn(ssn_raw) if ssn_raw else None
    if not ssn_masked:
        acr_ssn = _first(_ACR_SSN_RE, section_text) or _first(_ACR_SSN_RE, full_text)
        if acr_ssn:
            ssn_masked = f"***-**-{acr_ssn.split('-')[-1]}"
    if not ssn_masked:
        ssn_masked = mask_ssn(full_text)

    field_confidence: dict[str, float] = {}
    if consumer_name:
        field_confidence["consumer.name"] = _CONSUMER_CONFIDENCE
    if dob:
        field_confidence["consumer.date_of_birth"] = _CONSUMER_CONFIDENCE
    if ssn_masked:
        field_confidence["consumer.ssn_masked"] = _CONSUMER_CONFIDENCE

    if not (consumer_name or dob or ssn_masked):
        return None, field_confidence

    consumer_scores = [
        field_confidence[key]
        for key in ("consumer.name", "consumer.date_of_birth", "consumer.ssn_masked")
        if key in field_confidence
    ]
    return (
        ConsumerInfo(
            name=consumer_name,
            date_of_birth=dob,
            ssn_masked=ssn_masked,
            confidence=max(consumer_scores) if consumer_scores else 0.0,
        ),
        field_confidence,
    )


def extract_accounts(
    section_text: str,
    *,
    full_text: str | None = None,
) -> tuple[tuple[TradelineAccount, ...], dict[str, float]]:
    accounts: list[TradelineAccount] = []
    field_confidence: dict[str, float] = {}

    for index, match in enumerate(_TRADELINE_BLOCK_RE.finditer(section_text)):
        block = match.group(2)
        creditor = _first(_FURNISHER_RE, block)
        account_number_raw = _first(_ACCOUNT_IDENTIFIER_RE, block)
        account_type = _first(_PORTFOLIO_TYPE_RE, block)
        balance = parse_balance(_first(_CURRENT_BALANCE_RE, block))
        credit_limit = parse_balance(_first(_HIGH_CREDIT_RE, block))
        payment_status = _first(_ACCOUNT_STATUS_RE, block)
        open_date = _first(_DATE_OPENED_RE, block)
        date_reported = _first(_LAST_REPORTED_RE, block)
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

        account_scores = [field_confidence[key] for key in field_confidence if key.startswith(prefix)]
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
                bureau="equifax",
                confidence=max(account_scores) if account_scores else 0.0,
            )
        )

    if not accounts:
        acr_source = section_text or full_text or ""
        for index, match in enumerate(_ACR_ACCOUNT_RE.finditer(acr_source)):
            creditor = match.group(1).strip()
            date_reported = match.group(2).strip()
            balance = parse_balance(match.group(3))
            account_number_raw = match.group(4).strip()
            account_type = match.group(5).strip()
            open_date = match.group(6).strip()
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
            if open_date:
                field_confidence[f"{prefix}.open_date"] = _FIELD_CONFIDENCE
            if date_reported:
                field_confidence[f"{prefix}.date_reported"] = _FIELD_CONFIDENCE

            account_scores = [
                field_confidence[key] for key in field_confidence if key.startswith(prefix)
            ]
            accounts.append(
                TradelineAccount(
                    creditor_name=creditor,
                    account_number_masked=account_masked,
                    account_type=account_type,
                    balance=balance,
                    credit_limit=None,
                    payment_status=None,
                    open_date=open_date,
                    date_reported=date_reported,
                    bureau="equifax",
                    confidence=max(account_scores) if account_scores else 0.0,
                )
            )

    return tuple(accounts), field_confidence


def extract_inquiries(section_text: str) -> tuple[tuple[Inquiry, ...], dict[str, float]]:
    inquiries: list[Inquiry] = []
    field_confidence: dict[str, float] = {}

    for index, match in enumerate(_INQUIRY_BLOCK_RE.finditer(section_text)):
        block = match.group(2)
        creditor = _first(_REQUESTED_BY_RE, block)
        inquiry_date = _first(_DATE_OF_INQUIRY_RE, block)
        inquiry_type = _first(_PURPOSE_RE, block)
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

    return tuple(inquiries), field_confidence


def extract_public_records(section_text: str) -> tuple[tuple[PublicRecord, ...], dict[str, float]]:
    records: list[PublicRecord] = []
    field_confidence: dict[str, float] = {}

    for index, match in enumerate(_PUBLIC_RECORD_BLOCK_RE.finditer(section_text)):
        block = match.group(2)
        record_type = _first(_TYPE_RE, block)
        filing_date = _first(_FILED_RE, block)
        status = _first(_STATUS_RE, block)
        amount = parse_balance(_first(_AMOUNT_RE, block))
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
        acr_date = _first(_ACR_DATE_RE, full_text)
        if acr_date:
            report_date = _normalize_long_date(acr_date)
    if not report_date:
        return None, {}
    return report_date, {"report.report_date": _FIELD_CONFIDENCE}
