"""Document processing constants."""

from enum import StrEnum


class DocumentProcessingStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class DocumentType(StrEnum):
    CREDIT_REPORT = "credit_report"
    COLLECTION_LETTER = "collection_letter"
    BUREAU_RESPONSE = "bureau_response"
    IDENTITY_DOCUMENT = "identity_document"
    PROOF_OF_ADDRESS = "proof_of_address"
    SIGNED_CONSENT = "signed_consent"
    BANKRUPTCY = "bankruptcy"
    COURT_RECORD = "court_record"
    MEDICAL_COLLECTION = "medical_collection"
    UTILITY_BILL = "utility_bill"
    UNKNOWN = "unknown"


class ClassificationMethod(StrEnum):
    RULES = "rules"
    AI = "ai"


class MetadataStatus(StrEnum):
    PENDING = "pending"
    EXTRACTED = "extracted"
    FAILED = "failed"


class ExtractionMethod(StrEnum):
    RULES = "rules"
    AI = "ai"
    PARSER = "parser"


class MatchedEntityType(StrEnum):
    CASE = "case"
    ACCOUNT = "account"
    ORGANIZATION = "organization"
    PERSON = "person"


class ResolutionStatus(StrEnum):
    MATCHED = "matched"
    AMBIGUOUS = "ambiguous"
    UNMATCHED = "unmatched"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class ResolutionMethod(StrEnum):
    RULES = "rules"
    MANUAL = "manual"
    AI = "ai"


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
