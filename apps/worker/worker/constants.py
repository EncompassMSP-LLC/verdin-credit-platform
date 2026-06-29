"""Shared job type and status constants."""

from enum import StrEnum


class JobType(StrEnum):
    OCR = "ocr"
    DOCUMENT_CLASSIFY = "document_classify"
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
