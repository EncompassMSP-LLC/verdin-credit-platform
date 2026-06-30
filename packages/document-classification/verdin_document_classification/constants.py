"""Document classification constants."""

from enum import StrEnum


class DocumentType(StrEnum):
    CREDIT_REPORT = "credit_report"
    COLLECTION_LETTER = "collection_letter"
    BUREAU_RESPONSE = "bureau_response"
    IDENTITY_DOCUMENT = "identity_document"
    PROOF_OF_ADDRESS = "proof_of_address"
    BANKRUPTCY = "bankruptcy"
    COURT_RECORD = "court_record"
    MEDICAL_COLLECTION = "medical_collection"
    UTILITY_BILL = "utility_bill"
    UNKNOWN = "unknown"


class ClassificationMethod(StrEnum):
    RULES = "rules"
    AI = "ai"
