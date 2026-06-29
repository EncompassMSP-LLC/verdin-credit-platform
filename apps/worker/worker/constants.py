"""Shared job type and status constants."""

from enum import StrEnum


class JobType(StrEnum):
    OCR = "ocr"
    DOCUMENT_CLASSIFY = "document_classify"
    DOCUMENT_METADATA_EXTRACT = "document_metadata_extract"
    DOCUMENT_ENTITY_RESOLVE = "document_entity_resolve"
    REPORT_IMPORT = "report_import"
    AI_SUMMARY = "ai_summary"
    MONTHLY_REVIEW = "monthly_review"


class JobStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
