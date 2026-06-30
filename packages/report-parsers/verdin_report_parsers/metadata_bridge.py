"""Map canonical parsed credit reports into flat metadata fields."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from verdin_report_parsers.models import ParsedCreditReport


@dataclass(frozen=True, slots=True)
class BridgedMetadataFields:
    """Metadata shape consumed by entity resolution and document_metadata."""

    consumer_name: str | None
    bureau: str | None
    creditor: str | None
    collection_agency: str | None
    account_number_masked: str | None
    report_date: str | None
    open_date: str | None
    balance: float | None
    payment_status: str | None
    addresses: tuple[str, ...]
    phone_numbers: tuple[str, ...]
    ssn_masked: str | None
    confidence_score: float
    extraction_method: str


def _normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    if "/" in value:
        month, day, year = value.split("/")
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    return value


def bridge_parsed_report(report: ParsedCreditReport) -> BridgedMetadataFields:
    """Project a parsed report into metadata fields without bureau-specific logic."""
    consumer = report.consumer
    primary_account = report.accounts[0] if report.accounts else None
    primary_collection = report.collections[0] if report.collections else None

    addresses: list[str] = []
    phone_numbers: list[str] = []
    for item in report.personal_information:
        if item.field_name.lower() == "address":
            addresses.append(item.value)
        elif item.field_name.lower() == "phone":
            phone_numbers.append(item.value)

    parser_name = report.metadata.parser_name if report.metadata else "parser"
    field_confidence = report.metadata.field_confidence if report.metadata else {}
    layout_confidence = field_confidence.get("parser.layout_confidence")
    summary_confidence = report.summary.confidence if report.summary else None
    consumer_confidence = consumer.confidence if consumer else None
    confidence_candidates = [
        value
        for value in (layout_confidence, summary_confidence, consumer_confidence)
        if value is not None
    ]
    confidence_score = max(confidence_candidates) if confidence_candidates else 0.0

    report_date = None
    if report.metadata and "report.report_date" in field_confidence:
        report_date = _normalize_date(primary_account.date_reported if primary_account else None)
    elif primary_account and primary_account.date_reported:
        report_date = _normalize_date(primary_account.date_reported)

    return BridgedMetadataFields(
        consumer_name=consumer.name if consumer else None,
        bureau=report.bureau.value,
        creditor=primary_account.creditor_name if primary_account else None,
        collection_agency=primary_collection.agency_name if primary_collection else None,
        account_number_masked=(
            primary_account.account_number_masked if primary_account else None
        ),
        report_date=report_date,
        open_date=_normalize_date(primary_account.open_date if primary_account else None),
        balance=primary_account.balance if primary_account else None,
        payment_status=primary_account.payment_status if primary_account else None,
        addresses=tuple(addresses),
        phone_numbers=tuple(phone_numbers),
        ssn_masked=consumer.ssn_masked if consumer else None,
        confidence_score=confidence_score,
        extraction_method=f"parser:{parser_name}",
    )


def bridge_parsed_report_dict(report: dict[str, Any]) -> BridgedMetadataFields:
    """Bridge a serialized parsed report produced by ``ParsedCreditReport.as_dict``."""
    consumer = report.get("consumer") or {}
    accounts = report.get("accounts") or []
    collections = report.get("collections") or []
    personal_information = report.get("personal_information") or []
    metadata = report.get("metadata") or {}
    field_confidence = metadata.get("field_confidence") or {}
    summary = report.get("summary") or {}

    primary_account = accounts[0] if accounts else {}
    primary_collection = collections[0] if collections else {}

    addresses = [
        item["value"]
        for item in personal_information
        if item.get("field_name", "").lower() == "address" and item.get("value")
    ]
    phone_numbers = [
        item["value"]
        for item in personal_information
        if item.get("field_name", "").lower() == "phone" and item.get("value")
    ]

    parser_name = metadata.get("parser_name", "parser")
    confidence_candidates = [
        field_confidence.get("parser.layout_confidence"),
        summary.get("confidence"),
        consumer.get("confidence"),
    ]
    confidence_score = max(
        (value for value in confidence_candidates if value is not None),
        default=0.0,
    )

    report_date = None
    if primary_account.get("date_reported"):
        report_date = _normalize_date(primary_account["date_reported"])

    return BridgedMetadataFields(
        consumer_name=consumer.get("name"),
        bureau=report.get("bureau"),
        creditor=primary_account.get("creditor_name"),
        collection_agency=primary_collection.get("agency_name"),
        account_number_masked=primary_account.get("account_number_masked"),
        report_date=report_date,
        open_date=_normalize_date(primary_account.get("open_date")),
        balance=primary_account.get("balance"),
        payment_status=primary_account.get("payment_status"),
        addresses=tuple(addresses),
        phone_numbers=tuple(phone_numbers),
        ssn_masked=consumer.get("ssn_masked"),
        confidence_score=float(confidence_score),
        extraction_method=f"parser:{parser_name}",
    )
