"""Canonical parsed credit report domain models."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from verdin_report_parsers.constants import PARSED_CREDIT_REPORT_SCHEMA_VERSION, Bureau


@dataclass(frozen=True, slots=True)
class ConsumerInfo:
    name: str | None = None
    date_of_birth: str | None = None
    ssn_masked: str | None = None
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class TradelineAccount:
    creditor_name: str | None = None
    account_number_masked: str | None = None
    account_type: str | None = None
    balance: float | None = None
    credit_limit: float | None = None
    payment_status: str | None = None
    open_date: str | None = None
    date_reported: str | None = None
    bureau: str | None = None
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class Inquiry:
    creditor_name: str | None = None
    inquiry_date: str | None = None
    inquiry_type: str | None = None
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class PublicRecord:
    record_type: str | None = None
    filing_date: str | None = None
    status: str | None = None
    amount: float | None = None
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class Collection:
    agency_name: str | None = None
    original_creditor: str | None = None
    balance: float | None = None
    status: str | None = None
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class PersonalInformation:
    field_name: str
    value: str
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class ReportSummary:
    total_accounts: int = 0
    total_inquiries: int = 0
    total_public_records: int = 0
    total_collections: int = 0
    total_balance: float | None = None
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class ParseMetadata:
    parser_name: str
    parsed_at: str
    classification_type: str | None = None
    classification_confidence: float | None = None
    field_confidence: dict[str, float] = field(default_factory=dict)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    is_partial: bool = False

    @staticmethod
    def now(
        parser_name: str,
        *,
        classification_type: str | None = None,
        classification_confidence: float | None = None,
        field_confidence: dict[str, float] | None = None,
        warnings: tuple[str, ...] = (),
        is_partial: bool = False,
    ) -> "ParseMetadata":
        return ParseMetadata(
            parser_name=parser_name,
            parsed_at=datetime.now(UTC).isoformat(),
            classification_type=classification_type,
            classification_confidence=classification_confidence,
            field_confidence=field_confidence or {},
            warnings=warnings,
            is_partial=is_partial,
        )


@dataclass(frozen=True, slots=True)
class ParsedCreditReport:
    """Versioned canonical representation of a parsed bureau report."""

    schema_version: str = PARSED_CREDIT_REPORT_SCHEMA_VERSION
    report_id: str | None = None
    bureau: Bureau = Bureau.UNKNOWN
    consumer: ConsumerInfo | None = None
    accounts: tuple[TradelineAccount, ...] = field(default_factory=tuple)
    inquiries: tuple[Inquiry, ...] = field(default_factory=tuple)
    public_records: tuple[PublicRecord, ...] = field(default_factory=tuple)
    collections: tuple[Collection, ...] = field(default_factory=tuple)
    personal_information: tuple[PersonalInformation, ...] = field(default_factory=tuple)
    summary: ReportSummary | None = None
    metadata: ParseMetadata | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize for downstream consumers (entity resolution, storage)."""

        def _consumer() -> dict[str, Any] | None:
            if self.consumer is None:
                return None
            return {
                "name": self.consumer.name,
                "date_of_birth": self.consumer.date_of_birth,
                "ssn_masked": self.consumer.ssn_masked,
                "confidence": self.consumer.confidence,
            }

        return {
            "schema_version": self.schema_version,
            "report_id": self.report_id,
            "bureau": self.bureau.value,
            "consumer": _consumer(),
            "accounts": [
                {
                    "creditor_name": account.creditor_name,
                    "account_number_masked": account.account_number_masked,
                    "account_type": account.account_type,
                    "balance": account.balance,
                    "credit_limit": account.credit_limit,
                    "payment_status": account.payment_status,
                    "open_date": account.open_date,
                    "date_reported": account.date_reported,
                    "bureau": account.bureau,
                    "confidence": account.confidence,
                }
                for account in self.accounts
            ],
            "inquiries": [
                {
                    "creditor_name": inquiry.creditor_name,
                    "inquiry_date": inquiry.inquiry_date,
                    "inquiry_type": inquiry.inquiry_type,
                    "confidence": inquiry.confidence,
                }
                for inquiry in self.inquiries
            ],
            "public_records": [
                {
                    "record_type": record.record_type,
                    "filing_date": record.filing_date,
                    "status": record.status,
                    "amount": record.amount,
                    "confidence": record.confidence,
                }
                for record in self.public_records
            ],
            "collections": [
                {
                    "agency_name": collection.agency_name,
                    "original_creditor": collection.original_creditor,
                    "balance": collection.balance,
                    "status": collection.status,
                    "confidence": collection.confidence,
                }
                for collection in self.collections
            ],
            "personal_information": [
                {
                    "field_name": item.field_name,
                    "value": item.value,
                    "confidence": item.confidence,
                }
                for item in self.personal_information
            ],
            "summary": None
            if self.summary is None
            else {
                "total_accounts": self.summary.total_accounts,
                "total_inquiries": self.summary.total_inquiries,
                "total_public_records": self.summary.total_public_records,
                "total_collections": self.summary.total_collections,
                "total_balance": self.summary.total_balance,
                "confidence": self.summary.confidence,
            },
            "metadata": None
            if self.metadata is None
            else {
                "parser_name": self.metadata.parser_name,
                "parsed_at": self.metadata.parsed_at,
                "classification_type": self.metadata.classification_type,
                "classification_confidence": self.metadata.classification_confidence,
                "field_confidence": dict(self.metadata.field_confidence),
                "warnings": list(self.metadata.warnings),
                "is_partial": self.metadata.is_partial,
            },
        }
