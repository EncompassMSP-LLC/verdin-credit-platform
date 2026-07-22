"""Field extraction for IdentityIQ monitoring / tri-merge credit reports."""

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

_FIELD_CONFIDENCE = 0.90
_CONSUMER_CONFIDENCE = 0.93

_BUREAU_ALIASES: dict[str, str] = {
    "transunion": "transunion",
    "trans union": "transunion",
    "tu": "transunion",
    "experian": "experian",
    "ex": "experian",
    "equifax": "equifax",
    "eq": "equifax",
}

_NAME_RE = re.compile(r"^(?:Name|Consumer Name):\s*(.+)$", re.I | re.M)
_DOB_RE = re.compile(
    r"^(?:Date of Birth|DOB):\s*(\d{1,2}/\d{1,2}/\d{2,4})$",
    re.I | re.M,
)
_SSN_RE = re.compile(
    r"^(?:SSN|Social Security(?: Number)?):\s*([xX*\d-]{9,11})$",
    re.I | re.M,
)
_SSN_MASKED_RE = re.compile(
    r"(?:XXX|\*{3}|xxx)-(?:XX|\*{2}|xx)-(\d{4})",
    re.I,
)
_REPORT_DATE_RE = re.compile(
    r"^(?:Report Date|Date Generated|As Of):\s*(\d{1,2}/\d{1,2}/\d{2,4})$",
    re.I | re.M,
)

_ACCOUNT_START_RE = re.compile(
    r"^(?:Account Name|Creditor|Furnisher):\s*.+$|^Account\s+\d+\s*$",
    re.I | re.M,
)

_CREDITOR_RE = re.compile(r"^(?:Creditor|Account Name|Furnisher):\s*(.+)$", re.I | re.M)
_ACCOUNT_NUMBER_RE = re.compile(
    r"^(?:Account Number|Account #|Acct(?:\.| Number)?):\s*(.+)$",
    re.I | re.M,
)
_ACCOUNT_TYPE_RE = re.compile(r"^Account Type:\s*(.+)$", re.I | re.M)
_ORIGINAL_CREDITOR_RE = re.compile(r"^Original Creditor:\s*(.+)$", re.I | re.M)

_BUREAU_HEADER_RE = re.compile(
    r"^\s*(Trans\s*Union|TU)\s+(Experian|EX)\s+(Equifax|EQ)\s*$"
    r"|^\s*(Experian|EX)\s+(Trans\s*Union|TU)\s+(Equifax|EQ)\s*$"
    r"|^\s*(Equifax|EQ)\s+(Experian|EX)\s+(Trans\s*Union|TU)\s*$",
    re.I | re.M,
)

_TRI_FIELD_RE = re.compile(
    r"^(Balance|High Balance|High Credit|Credit Limit|Past Due(?: Amount)?|"
    r"Account Status|Payment Status|Status|Date Opened|Date Closed|"
    r"Date Reported|Date of First Delinquency|DOFD|Payment History|Remarks?)\s+"
    r"(\$?[\d,]+(?:\.\d{2})?|--|N/?A|Current|Open|Closed|Paid|"
    r"Charge[\s-]?Off|Collection|Late\s+\d+|Never late|"
    r"\d{1,2}/\d{1,2}/\d{2,4}|[A-Za-z0-9*C\- /]{1,40})"
    r"\s+"
    r"(\$?[\d,]+(?:\.\d{2})?|--|N/?A|Current|Open|Closed|Paid|"
    r"Charge[\s-]?Off|Collection|Late\s+\d+|Never late|"
    r"\d{1,2}/\d{1,2}/\d{2,4}|[A-Za-z0-9*C\- /]{1,40})"
    r"\s+"
    r"(\$?[\d,]+(?:\.\d{2})?|--|N/?A|Current|Open|Closed|Paid|"
    r"Charge[\s-]?Off|Collection|Late\s+\d+|Never late|"
    r"\d{1,2}/\d{1,2}/\d{2,4}|[A-Za-z0-9*C\- /]{1,40})"
    r"\s*$",
    re.I | re.M,
)

_SINGLE_BALANCE_RE = re.compile(r"^Balance:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_SINGLE_LIMIT_RE = re.compile(r"^Credit Limit:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_SINGLE_HIGH_RE = re.compile(r"^(?:High Credit|High Balance):\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_SINGLE_PAST_DUE_RE = re.compile(r"^Past Due(?: Amount)?:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_SINGLE_STATUS_RE = re.compile(r"^(?:Account Status|Status):\s*(.+)$", re.I | re.M)
_SINGLE_PAYMENT_RE = re.compile(r"^Payment Status:\s*(.+)$", re.I | re.M)
_SINGLE_OPEN_RE = re.compile(r"^Date Opened:\s*(\d{1,2}/\d{1,2}/\d{2,4})$", re.I | re.M)
_SINGLE_CLOSED_RE = re.compile(r"^Date Closed:\s*(\d{1,2}/\d{1,2}/\d{2,4})$", re.I | re.M)
_SINGLE_REPORTED_RE = re.compile(r"^Date Reported:\s*(\d{1,2}/\d{1,2}/\d{2,4})$", re.I | re.M)
_SINGLE_DOFD_RE = re.compile(
    r"^(?:Date of First Delinquency|DOFD):\s*(\d{1,2}/\d{1,2}/\d{2,4})$",
    re.I | re.M,
)
_SINGLE_HISTORY_RE = re.compile(r"^Payment History:\s*(.+)$", re.I | re.M)
_SINGLE_REMARKS_RE = re.compile(r"^Remarks?:\s*(.+)$", re.I | re.M)
_SINGLE_BUREAU_RE = re.compile(r"^Bureau:\s*(.+)$", re.I | re.M)

_INQUIRY_BLOCK_RE = re.compile(
    r"^Inquiry\s+(\d+)\s*\n(.*?)(?=^Inquiry\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_INQUIRED_BY_RE = re.compile(r"^(?:Inquired By|Creditor|Name):\s*(.+)$", re.I | re.M)
_INQUIRY_DATE_RE = re.compile(
    r"^(?:Inquiry Date|Date):\s*(\d{1,2}/\d{1,2}/\d{2,4})$",
    re.I | re.M,
)
_INQUIRY_TYPE_RE = re.compile(r"^(?:Inquiry Type|Type):\s*(.+)$", re.I | re.M)
_INQUIRY_BUREAU_RE = re.compile(r"^Bureau:\s*(.+)$", re.I | re.M)

_PUBLIC_RECORD_BLOCK_RE = re.compile(
    r"^Record\s+(\d+)\s*\n(.*?)(?=^Record\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_RECORD_TYPE_RE = re.compile(r"^Record Type:\s*(.+)$", re.I | re.M)
_FILING_DATE_RE = re.compile(r"^Filing Date:\s*(\d{1,2}/\d{1,2}/\d{2,4})$", re.I | re.M)
_RECORD_STATUS_RE = re.compile(r"^Status:\s*(.+)$", re.I | re.M)
_RECORD_AMOUNT_RE = re.compile(r"^Amount:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)

_COLLECTION_BLOCK_RE = re.compile(
    r"^Collection\s+(\d+)\s*\n(.*?)(?=^Collection\s+\d+\s*$|\Z)",
    re.I | re.M | re.S,
)
_AGENCY_RE = re.compile(r"^(?:Collection Agency|Agency):\s*(.+)$", re.I | re.M)
_COLLECTION_BALANCE_RE = re.compile(r"^Balance:\s*\$?([\d,]+\.?\d*)$", re.I | re.M)
_COLLECTION_STATUS_RE = re.compile(r"^Status:\s*(.+)$", re.I | re.M)

_EMPTY_VALUES = {"", "--", "-", "n/a", "na", "none", "null"}


def _first(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def _normalize_bureau(raw: str) -> str | None:
    key = re.sub(r"\s+", " ", raw.strip().lower())
    return _BUREAU_ALIASES.get(key)


def _is_empty(value: str | None) -> bool:
    if value is None:
        return True
    return value.strip().lower() in _EMPTY_VALUES


def _money_or_none(value: str | None) -> float | None:
    if _is_empty(value):
        return None
    return parse_balance(value)


def _text_or_none(value: str | None) -> str | None:
    if _is_empty(value):
        return None
    return value.strip() if value else None


def extract_consumer(
    section_text: str,
    full_text: str,
) -> tuple[ConsumerInfo | None, dict[str, float]]:
    name = _first(_NAME_RE, section_text) or _first(_NAME_RE, full_text)
    dob = _first(_DOB_RE, section_text) or _first(_DOB_RE, full_text)
    ssn_raw = _first(_SSN_RE, section_text) or _first(_SSN_RE, full_text)
    ssn_masked = None
    if ssn_raw:
        masked_match = _SSN_MASKED_RE.search(ssn_raw)
        if masked_match:
            ssn_masked = f"***-**-{masked_match.group(1)}"
        else:
            ssn_masked = mask_ssn(ssn_raw)
    if ssn_masked is None:
        masked_match = _SSN_MASKED_RE.search(section_text) or _SSN_MASKED_RE.search(full_text)
        if masked_match:
            ssn_masked = f"***-**-{masked_match.group(1)}"
        else:
            ssn_masked = mask_ssn(full_text)

    field_confidence: dict[str, float] = {}
    if name:
        field_confidence["consumer.name"] = _CONSUMER_CONFIDENCE
    if dob:
        field_confidence["consumer.date_of_birth"] = _CONSUMER_CONFIDENCE
    if ssn_masked:
        field_confidence["consumer.ssn_masked"] = _CONSUMER_CONFIDENCE

    if not (name or dob or ssn_masked):
        return None, field_confidence

    scores = list(field_confidence.values())
    return (
        ConsumerInfo(
            name=name,
            date_of_birth=dob,
            ssn_masked=ssn_masked,
            confidence=max(scores) if scores else 0.0,
        ),
        field_confidence,
    )


def extract_report_date(text: str) -> tuple[str | None, dict[str, float]]:
    report_date = _first(_REPORT_DATE_RE, text)
    if report_date:
        return report_date, {"report.date": _FIELD_CONFIDENCE}
    return None, {}


def _default_bureau_order(block: str) -> tuple[str, str, str]:
    match = _BUREAU_HEADER_RE.search(block)
    if not match:
        return ("transunion", "experian", "equifax")
    labels = [g for g in match.groups() if g]
    normalized = tuple(_normalize_bureau(label) or label.lower() for label in labels[:3])
    if len(normalized) == 3 and all(normalized):
        return normalized  # type: ignore[return-value]
    return ("transunion", "experian", "equifax")


def _tri_field_map(block: str) -> dict[str, tuple[str | None, str | None, str | None]]:
    fields: dict[str, tuple[str | None, str | None, str | None]] = {}
    for match in _TRI_FIELD_RE.finditer(block):
        key = match.group(1).strip().lower()
        fields[key] = (
            _text_or_none(match.group(2)),
            _text_or_none(match.group(3)),
            _text_or_none(match.group(4)),
        )
    return fields


def _pick_tri(
    fields: dict[str, tuple[str | None, str | None, str | None]],
    *keys: str,
    index: int,
) -> str | None:
    for key in keys:
        values = fields.get(key)
        if values is None:
            continue
        value = values[index]
        if not _is_empty(value):
            return value
    return None


def _append_account(
    accounts: list[TradelineAccount],
    field_confidence: dict[str, float],
    *,
    creditor: str | None,
    account_masked: str | None,
    account_type: str | None,
    original_creditor: str | None,
    bureau: str,
    balance: float | None,
    credit_limit: float | None,
    high_credit: float | None,
    past_due_amount: float | None,
    account_status: str | None,
    payment_status: str | None,
    open_date: str | None,
    date_closed: str | None,
    date_reported: str | None,
    date_first_delinquency: str | None,
    payment_history: str | None,
    remarks: str | None,
) -> None:
    if not any(
        (
            creditor,
            account_masked,
            balance is not None,
            account_status,
            payment_status,
        )
    ):
        return

    index = len(accounts)
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
    if high_credit is not None:
        field_confidence[f"{prefix}.high_credit"] = _FIELD_CONFIDENCE
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
    field_confidence[f"{prefix}.bureau"] = _FIELD_CONFIDENCE

    scores = [field_confidence[key] for key in field_confidence if key.startswith(prefix)]
    accounts.append(
        TradelineAccount(
            creditor_name=creditor,
            account_number_masked=account_masked,
            account_type=account_type,
            account_status=account_status or payment_status,
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
            original_creditor=original_creditor,
            bureau=bureau,
            confidence=max(scores) if scores else 0.0,
        )
    )


def _split_account_blocks(source: str) -> list[str]:
    starts = [match.start() for match in _ACCOUNT_START_RE.finditer(source)]
    if not starts:
        if _CREDITOR_RE.search(source) or _ACCOUNT_NUMBER_RE.search(source):
            return [source]
        return []

    blocks: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(source)
        block = source[start:end].strip()
        if block:
            blocks.append(block)
    return blocks


def extract_accounts(
    section_text: str,
    *,
    full_text: str | None = None,
) -> tuple[tuple[TradelineAccount, ...], dict[str, float]]:
    source = section_text.strip() or (full_text or "")
    accounts: list[TradelineAccount] = []
    field_confidence: dict[str, float] = {}

    for block in _split_account_blocks(source):
        creditor = _first(_CREDITOR_RE, block)
        account_number_raw = _first(_ACCOUNT_NUMBER_RE, block)
        account_masked = (
            mask_account_number(account_number_raw) if account_number_raw else None
        )
        account_type = _first(_ACCOUNT_TYPE_RE, block)
        original_creditor = _first(_ORIGINAL_CREDITOR_RE, block)
        tri_fields = _tri_field_map(block)
        bureau_order = _default_bureau_order(block)

        if tri_fields:
            for index, bureau in enumerate(bureau_order):
                balance = _money_or_none(_pick_tri(tri_fields, "balance", index=index))
                credit_limit = _money_or_none(
                    _pick_tri(tri_fields, "credit limit", index=index)
                )
                high_credit = _money_or_none(
                    _pick_tri(tri_fields, "high balance", "high credit", index=index)
                )
                past_due = _money_or_none(
                    _pick_tri(tri_fields, "past due", "past due amount", index=index)
                )
                account_status = _pick_tri(
                    tri_fields, "account status", "status", index=index
                )
                payment_status = _pick_tri(tri_fields, "payment status", index=index)
                open_date = _pick_tri(tri_fields, "date opened", index=index)
                date_closed = _pick_tri(tri_fields, "date closed", index=index)
                date_reported = _pick_tri(tri_fields, "date reported", index=index)
                dofd = _pick_tri(
                    tri_fields, "date of first delinquency", "dofd", index=index
                )
                payment_history = _pick_tri(tri_fields, "payment history", index=index)
                remarks = _pick_tri(tri_fields, "remarks", "remark", index=index)

                # Skip empty bureau columns (tradeline not reported on that CRA).
                if all(
                    value is None
                    for value in (
                        balance,
                        credit_limit,
                        high_credit,
                        past_due,
                        account_status,
                        payment_status,
                        open_date,
                    )
                ):
                    continue

                _append_account(
                    accounts,
                    field_confidence,
                    creditor=creditor,
                    account_masked=account_masked,
                    account_type=account_type,
                    original_creditor=original_creditor,
                    bureau=bureau,
                    balance=balance,
                    credit_limit=credit_limit,
                    high_credit=high_credit,
                    past_due_amount=past_due,
                    account_status=account_status,
                    payment_status=payment_status,
                    open_date=open_date,
                    date_closed=date_closed,
                    date_reported=date_reported,
                    date_first_delinquency=dofd,
                    payment_history=payment_history,
                    remarks=remarks,
                )
            continue

        # Single-bureau / collapsed IdentityIQ account block.
        bureau_raw = _first(_SINGLE_BUREAU_RE, block)
        bureau = _normalize_bureau(bureau_raw) if bureau_raw else "unknown"
        _append_account(
            accounts,
            field_confidence,
            creditor=creditor,
            account_masked=account_masked,
            account_type=account_type,
            original_creditor=original_creditor,
            bureau=bureau or "unknown",
            balance=_money_or_none(_first(_SINGLE_BALANCE_RE, block)),
            credit_limit=_money_or_none(_first(_SINGLE_LIMIT_RE, block)),
            high_credit=_money_or_none(_first(_SINGLE_HIGH_RE, block)),
            past_due_amount=_money_or_none(_first(_SINGLE_PAST_DUE_RE, block)),
            account_status=_first(_SINGLE_STATUS_RE, block),
            payment_status=_first(_SINGLE_PAYMENT_RE, block),
            open_date=_first(_SINGLE_OPEN_RE, block),
            date_closed=_first(_SINGLE_CLOSED_RE, block),
            date_reported=_first(_SINGLE_REPORTED_RE, block),
            date_first_delinquency=_first(_SINGLE_DOFD_RE, block),
            payment_history=_first(_SINGLE_HISTORY_RE, block),
            remarks=_first(_SINGLE_REMARKS_RE, block),
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
        bureau = _first(_INQUIRY_BUREAU_RE, block)
        if bureau and inquiry_type:
            inquiry_type = f"{inquiry_type} ({bureau})"
        elif bureau and not inquiry_type:
            inquiry_type = bureau

        prefix = f"inquiries[{index}]"
        if creditor:
            field_confidence[f"{prefix}.creditor_name"] = _FIELD_CONFIDENCE
        if inquiry_date:
            field_confidence[f"{prefix}.inquiry_date"] = _FIELD_CONFIDENCE
        if inquiry_type:
            field_confidence[f"{prefix}.inquiry_type"] = _FIELD_CONFIDENCE
        scores = [field_confidence[key] for key in field_confidence if key.startswith(prefix)]
        inquiries.append(
            Inquiry(
                creditor_name=creditor,
                inquiry_date=inquiry_date,
                inquiry_type=inquiry_type,
                confidence=max(scores) if scores else 0.0,
            )
        )
    return tuple(inquiries), field_confidence


def extract_public_records(
    section_text: str,
) -> tuple[tuple[PublicRecord, ...], dict[str, float]]:
    records: list[PublicRecord] = []
    field_confidence: dict[str, float] = {}
    for index, match in enumerate(_PUBLIC_RECORD_BLOCK_RE.finditer(section_text)):
        block = match.group(2)
        record_type = _first(_RECORD_TYPE_RE, block)
        filing_date = _first(_FILING_DATE_RE, block)
        status = _first(_RECORD_STATUS_RE, block)
        amount = _money_or_none(_first(_RECORD_AMOUNT_RE, block))
        prefix = f"public_records[{index}]"
        if record_type:
            field_confidence[f"{prefix}.record_type"] = _FIELD_CONFIDENCE
        if filing_date:
            field_confidence[f"{prefix}.filing_date"] = _FIELD_CONFIDENCE
        if status:
            field_confidence[f"{prefix}.status"] = _FIELD_CONFIDENCE
        if amount is not None:
            field_confidence[f"{prefix}.amount"] = _FIELD_CONFIDENCE
        scores = [field_confidence[key] for key in field_confidence if key.startswith(prefix)]
        records.append(
            PublicRecord(
                record_type=record_type,
                filing_date=filing_date,
                status=status,
                amount=amount,
                confidence=max(scores) if scores else 0.0,
            )
        )
    return tuple(records), field_confidence


def extract_collections(
    section_text: str,
) -> tuple[tuple[Collection, ...], dict[str, float]]:
    collections: list[Collection] = []
    field_confidence: dict[str, float] = {}
    for index, match in enumerate(_COLLECTION_BLOCK_RE.finditer(section_text)):
        block = match.group(2)
        agency = _first(_AGENCY_RE, block)
        original = _first(_ORIGINAL_CREDITOR_RE, block)
        balance = _money_or_none(_first(_COLLECTION_BALANCE_RE, block))
        status = _first(_COLLECTION_STATUS_RE, block)
        prefix = f"collections[{index}]"
        if agency:
            field_confidence[f"{prefix}.agency_name"] = _FIELD_CONFIDENCE
        if original:
            field_confidence[f"{prefix}.original_creditor"] = _FIELD_CONFIDENCE
        if balance is not None:
            field_confidence[f"{prefix}.balance"] = _FIELD_CONFIDENCE
        if status:
            field_confidence[f"{prefix}.status"] = _FIELD_CONFIDENCE
        scores = [field_confidence[key] for key in field_confidence if key.startswith(prefix)]
        collections.append(
            Collection(
                agency_name=agency,
                original_creditor=original,
                balance=balance,
                status=status,
                confidence=max(scores) if scores else 0.0,
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
    summary_confidence = 0.85 if accounts or inquiries else 0.4
    field_confidence["summary.total_accounts"] = summary_confidence
    return ReportSummary(
        total_accounts=len(accounts),
        total_inquiries=len(inquiries),
        total_public_records=len(public_records),
        total_collections=len(collections),
        total_balance=sum(balances) if balances else None,
        confidence=summary_confidence,
    )
