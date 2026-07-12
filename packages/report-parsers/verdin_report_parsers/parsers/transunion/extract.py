"""Field extraction for TransUnion 2026 consumer credit report layouts."""

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

_NAME_RE = re.compile(r"^Name:\s*(.+)$", re.I | re.M)
_DOB_RE = re.compile(r"^Date of Birth:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_SSN_RE = re.compile(r"^Social Security Number:\s*(\d{3}-\d{2}-\d{4})$", re.I | re.M)

_ACCOUNT_BLOCK_RE = re.compile(
    r"^Account\s+(\d+)\s*\n(.*?)(?=^Account\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_SUBSCRIBER_RE = re.compile(r"^Subscriber:\s*(.+)$", re.I | re.M)
_ACCOUNT_NUMBER_RE = re.compile(r"^Account Number:\s*(.+)$", re.I | re.M)
_ACCOUNT_TYPE_RE = re.compile(r"^Account Type:\s*(.+)$", re.I | re.M)
_BALANCE_RE = re.compile(r"^Balance:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_HIGH_CREDIT_RE = re.compile(r"^High Credit:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_CREDIT_LIMIT_RE = re.compile(r"^Credit Limit:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_PAST_DUE_RE = re.compile(r"^Past Due(?: Amount)?:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_ACCOUNT_STATUS_RE = re.compile(r"^Account Status:\s*(.+)$", re.I | re.M)
_PAYMENT_STATUS_RE = re.compile(r"^Payment Status:\s*(.+)$", re.I | re.M)
_DATE_OPENED_RE = re.compile(r"^Date Opened:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_DATE_CLOSED_RE = re.compile(r"^Date Closed:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_DATE_UPDATED_RE = re.compile(r"^Date Updated:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_DOFD_RE = re.compile(
    r"^(?:Date of First Delinquency|First Delinquency|DOFD):\s*(\d{1,2}/\d{1,2}/\d{4})$",
    re.I | re.M,
)
_REMARKS_RE = re.compile(r"^Remarks?:\s*(.+)$", re.I | re.M)
_PAYMENT_HISTORY_RE = re.compile(r"^Payment History:\s*(.+)$", re.I | re.M)

_INQUIRY_BLOCK_RE = re.compile(
    r"^Inquiry\s+(\d+)\s*\n(.*?)(?=^Inquiry\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_INQUIRED_BY_RE = re.compile(r"^Inquired By:\s*(.+)$", re.I | re.M)
_INQUIRY_DATE_RE = re.compile(r"^Inquiry Date:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_INQUIRY_TYPE_RE = re.compile(r"^Inquiry Type:\s*(.+)$", re.I | re.M)

_PUBLIC_RECORD_BLOCK_RE = re.compile(
    r"^Public Record\s+(\d+)\s*\n(.*?)(?=^Public Record\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_RECORD_TYPE_RE = re.compile(r"^Record Type:\s*(.+)$", re.I | re.M)
_FILED_RE = re.compile(r"^Filed:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_STATUS_RE = re.compile(r"^Status:\s*(.+)$", re.I | re.M)
_AMOUNT_RE = re.compile(r"^Amount:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)

_COLLECTION_BLOCK_RE = re.compile(
    r"^Collection\s+(\d+)\s*\n(.*?)(?=^Collection\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_AGENCY_RE = re.compile(r"^Agency:\s*(.+)$", re.I | re.M)
_ORIGINAL_CREDITOR_RE = re.compile(r"^Original Creditor:\s*(.+)$", re.I | re.M)
_COLLECTION_BALANCE_RE = re.compile(r"^Balance:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_COLLECTION_STATUS_RE = re.compile(r"^Status:\s*(.+)$", re.I | re.M)

_REPORT_DATE_RE = re.compile(r"^Report Date:\s*(\d{1,2}/\d{1,2}/\d{4})$", re.I | re.M)
_ACR_REPORT_DATE_RE = re.compile(r"Credit Report Date\s*\n(\d{1,2}/\d{1,2}/\d{4})", re.I)
_DATE_CREATED_RE = re.compile(r"Date Created:\s*\n(\d{1,2}/\d{1,2}/\d{4})", re.I)
_PREPARED_FOR_RE = re.compile(
    r"Personal Credit Report for:\s*\n([A-Z][A-Z .'-]{2,80})",
    re.I | re.M,
)
_ACR_NAME_RE = re.compile(r"^Name\s*\n([A-Z][A-Z .'-]{2,80})", re.I | re.M)
_ACR_ACCOUNT_MARKER = re.compile(r"Account Name\s*\n", re.I)
_ACR_INFO_MARKER = re.compile(r"Account Information\s*\n", re.I)
_ACR_BALANCE_RE = re.compile(r"Balance\s+\$?([\d,]+)", re.I)
_ACR_OPENED_RE = re.compile(r"Date Opened\s+(\d{1,2}/\d{1,2}/\d{4})", re.I)
_ACR_STATUS_RE = re.compile(r"Pay Status\s+>?([^<\n]+?)<?", re.I)
_ACR_TYPE_RE = re.compile(r"Account Type\s+(.+?)(?:\s+Loan Type|\n)", re.I)
_ACR_UPDATED_RE = re.compile(r"Date Updated\s+(\d{1,2}/\d{1,2}/\d{4})", re.I)


def _first(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def extract_consumer(section_text: str, full_text: str) -> tuple[ConsumerInfo | None, dict[str, float]]:
    name = (
        _first(_NAME_RE, section_text)
        or _first(_ACR_NAME_RE, section_text)
        or _first(_PREPARED_FOR_RE, full_text)
    )
    dob = _first(_DOB_RE, section_text)
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

    consumer_scores = [
        field_confidence[key]
        for key in ("consumer.name", "consumer.date_of_birth", "consumer.ssn_masked")
        if key in field_confidence
    ]
    return (
        ConsumerInfo(
            name=name,
            date_of_birth=dob,
            ssn_masked=ssn_masked,
            confidence=max(consumer_scores) if consumer_scores else 0.0,
        ),
        field_confidence,
    )


def _parse_tu_acr_header(header_text: str) -> tuple[str | None, str | None]:
    lines = [line.strip() for line in header_text.splitlines() if line.strip()]
    if not lines:
        return None, None
    if len(lines) >= 2 and re.search(r"[*Xx\d]{4,}$", lines[1]):
        creditor = lines[0]
        account_number_raw = lines[1]
        return creditor, account_number_raw
    combined = lines[0]
    account_number_raw = combined.split()[-1] if combined else None
    creditor = re.sub(r"\s+[A-Z0-9*]{4,}$", "", combined).strip()
    return creditor or None, account_number_raw


def _extract_tu_acr_accounts(text: str) -> list[tuple[str, str, str]]:
    """Return (creditor, account_number_raw, info_block) tuples from ACR layout."""
    results: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()

    def _add(creditor: str | None, account_number_raw: str, info_block: str) -> None:
        if not creditor:
            return
        key = (creditor, account_number_raw)
        if key in seen:
            return
        seen.add(key)
        results.append((creditor, account_number_raw, info_block))

    for match in _ACR_ACCOUNT_MARKER.finditer(text):
        tail = text[match.end() :]
        info_match = _ACR_INFO_MARKER.search(tail)
        if not info_match:
            continue
        header_text = tail[: info_match.start()]
        info_block = tail[info_match.end() : info_match.end() + 2500]
        creditor, account_number_raw = _parse_tu_acr_header(header_text)
        _add(creditor, account_number_raw or "", info_block)

    for info_match in _ACR_INFO_MARKER.finditer(text):
        before = text[max(0, info_match.start() - 400) : info_match.start()]
        if re.search(r"Account Name\s*\n", before, re.I):
            continue
        line_match = re.search(
            r"(?:^|\n)([A-Z][A-Z0-9 &.'/-]{3,80}?)\s+([A-Z0-9*]{4,})\s*$",
            before,
            re.M,
        )
        if not line_match:
            continue
        info_block = text[info_match.end() : info_match.end() + 2500]
        _add(line_match.group(1).strip(), line_match.group(2).strip(), info_block)

    return results


def extract_accounts(
    section_text: str,
    *,
    full_text: str | None = None,
) -> tuple[tuple[TradelineAccount, ...], dict[str, float]]:
    accounts: list[TradelineAccount] = []
    field_confidence: dict[str, float] = {}

    for index, match in enumerate(_ACCOUNT_BLOCK_RE.finditer(section_text)):
        block = match.group(2)
        creditor = _first(_SUBSCRIBER_RE, block)
        account_number_raw = _first(_ACCOUNT_NUMBER_RE, block)
        account_type = _first(_ACCOUNT_TYPE_RE, block)
        balance = parse_balance(_first(_BALANCE_RE, block))
        high_credit = parse_balance(_first(_HIGH_CREDIT_RE, block))
        credit_limit = parse_balance(_first(_CREDIT_LIMIT_RE, block))
        past_due_amount = parse_balance(_first(_PAST_DUE_RE, block))
        account_status = _first(_ACCOUNT_STATUS_RE, block)
        payment_status = _first(_PAYMENT_STATUS_RE, block) or account_status
        open_date = _first(_DATE_OPENED_RE, block)
        date_closed = _first(_DATE_CLOSED_RE, block)
        date_reported = _first(_DATE_UPDATED_RE, block)
        date_first_delinquency = _first(_DOFD_RE, block)
        remarks = _first(_REMARKS_RE, block)
        payment_history = _first(_PAYMENT_HISTORY_RE, block)
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
        if high_credit is not None:
            field_confidence[f"{prefix}.high_credit"] = _FIELD_CONFIDENCE
        if credit_limit is not None:
            field_confidence[f"{prefix}.credit_limit"] = _FIELD_CONFIDENCE
        if past_due_amount is not None:
            field_confidence[f"{prefix}.past_due_amount"] = _FIELD_CONFIDENCE
        if account_status:
            field_confidence[f"{prefix}.account_status"] = _FIELD_CONFIDENCE
        if payment_status:
            field_confidence[f"{prefix}.payment_status"] = _FIELD_CONFIDENCE
        if open_date:
            field_confidence[f"{prefix}.open_date"] = _FIELD_CONFIDENCE
        if date_closed:
            field_confidence[f"{prefix}.date_closed"] = _FIELD_CONFIDENCE
        if date_reported:
            field_confidence[f"{prefix}.date_reported"] = _FIELD_CONFIDENCE
        if date_first_delinquency:
            field_confidence[f"{prefix}.date_first_delinquency"] = _FIELD_CONFIDENCE
        if remarks:
            field_confidence[f"{prefix}.remarks"] = _FIELD_CONFIDENCE
        if payment_history:
            field_confidence[f"{prefix}.payment_history"] = _FIELD_CONFIDENCE

        account_scores = [field_confidence[key] for key in field_confidence if key.startswith(prefix)]
        accounts.append(
            TradelineAccount(
                creditor_name=creditor,
                account_number_masked=account_masked,
                account_type=account_type,
                account_status=account_status,
                balance=balance,
                past_due_amount=past_due_amount,
                high_credit=high_credit,
                credit_limit=credit_limit,
                payment_status=payment_status,
                payment_history=payment_history,
                remarks=remarks,
                open_date=open_date,
                date_closed=date_closed,
                date_reported=date_reported,
                date_first_delinquency=date_first_delinquency,
                bureau="transunion",
                confidence=max(account_scores) if account_scores else 0.0,
            )
        )

    if not accounts:
        acr_source = section_text or full_text or ""
        for index, (creditor, account_number_raw, block) in enumerate(
            _extract_tu_acr_accounts(acr_source)
        ):
            balance = parse_balance(_first(_ACR_BALANCE_RE, block))
            open_date = _first(_ACR_OPENED_RE, block)
            payment_status = _first(_ACR_STATUS_RE, block)
            account_type = _first(_ACR_TYPE_RE, block)
            date_reported = _first(_ACR_UPDATED_RE, block)
            account_masked = (
                mask_account_number(account_number_raw) if account_number_raw else None
            )

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
                    payment_status=payment_status,
                    open_date=open_date,
                    date_reported=date_reported,
                    bureau="transunion",
                    confidence=max(account_scores) if account_scores else 0.0,
                )
            )

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

    return tuple(inquiries), field_confidence


def extract_public_records(section_text: str) -> tuple[tuple[PublicRecord, ...], dict[str, float]]:
    records: list[PublicRecord] = []
    field_confidence: dict[str, float] = {}

    for index, match in enumerate(_PUBLIC_RECORD_BLOCK_RE.finditer(section_text)):
        block = match.group(2)
        record_type = _first(_RECORD_TYPE_RE, block)
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
        report_date = _first(_ACR_REPORT_DATE_RE, full_text) or _first(_DATE_CREATED_RE, full_text)
    if not report_date:
        return None, {}
    return report_date, {"report.report_date": _FIELD_CONFIDENCE}
