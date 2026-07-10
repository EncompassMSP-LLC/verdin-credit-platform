"""Parser contracts and input document shape."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from verdin_report_parsers.models import ParsedCreditReport


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    """Inputs available to every credit report parser after classification."""

    ocr_text: str | None
    file_name: str
    title: str
    mime_type: str | None
    document_type: str | None = None
    classification_confidence: float | None = None
    document_id: str | None = None

    def searchable_text(self) -> str:
        parts = [self.title, self.file_name]
        if self.ocr_text:
            parts.append(self.ocr_text)
        return " ".join(parts).lower()

    def source_text(self) -> str:
        """Original-case text for field extraction."""
        parts = [self.title, self.file_name]
        if self.ocr_text:
            parts.append(self.ocr_text)
        return "\n\n".join(parts)


@runtime_checkable
class CreditReportParser(Protocol):
    """Evaluate and parse a classified document into a structured credit report."""

    name: str

    def can_parse(self, document: ParsedDocument) -> float:
        """Return a confidence score in ``[0.0, 1.0]``; ``0.0`` means no match."""

    def parse(self, document: ParsedDocument) -> ParsedCreditReport: ...
