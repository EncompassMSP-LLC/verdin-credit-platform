"""Document processing constants."""

from enum import StrEnum


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
