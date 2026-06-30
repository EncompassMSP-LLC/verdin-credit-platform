"""Metadata extraction contracts."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ExtractionContext:
    ocr_text: str | None
    file_name: str
    title: str
    document_type: str | None


@dataclass(frozen=True, slots=True)
class ExtractedMetadata:
    consumer_name: str | None = None
    bureau: str | None = None
    creditor: str | None = None
    collection_agency: str | None = None
    account_number_masked: str | None = None
    report_date: str | None = None
    open_date: str | None = None
    balance: float | None = None
    payment_status: str | None = None
    addresses: tuple[str, ...] = field(default_factory=tuple)
    phone_numbers: tuple[str, ...] = field(default_factory=tuple)
    ssn_masked: str | None = None
    confidence_score: float = 0.0
    field_confidence: dict[str, float] = field(default_factory=dict)

    def as_resolution_metadata(self) -> dict[str, Any]:
        return {
            "consumer_name": self.consumer_name,
            "bureau": self.bureau,
            "creditor": self.creditor,
            "collection_agency": self.collection_agency,
            "account_number_masked": self.account_number_masked,
            "report_date": self.report_date,
            "open_date": self.open_date,
            "balance": self.balance,
            "payment_status": self.payment_status,
            "addresses": list(self.addresses),
            "phone_numbers": list(self.phone_numbers),
            "ssn_masked": self.ssn_masked,
        }
