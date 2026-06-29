"""Document processing constants."""

from enum import StrEnum

from verdin_document_classification.constants import (
    ClassificationMethod,
    ClassificationStatus,
    DocumentType,
)

__all__ = [
    "ClassificationMethod",
    "ClassificationStatus",
    "DocumentProcessingStatus",
    "DocumentType",
    "OCR_MIME_TYPES",
    "is_ocr_eligible",
]


class DocumentProcessingStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


OCR_MIME_TYPES = frozenset(
    {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/tiff",
    }
)


def is_ocr_eligible(mime_type: str | None) -> bool:
    return mime_type in OCR_MIME_TYPES
