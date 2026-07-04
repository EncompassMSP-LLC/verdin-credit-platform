"""Shared job type and status constants."""

from enum import StrEnum


class JobType(StrEnum):
    OCR = "ocr"
    DOCUMENT_CLASSIFY = "document_classify"
    DOCUMENT_CREDIT_REPORT_PARSE = "document_credit_report_parse"
    DOCUMENT_METADATA_EXTRACT = "document_metadata_extract"
    DOCUMENT_ENTITY_RESOLVE = "document_entity_resolve"
    REPORT_IMPORT = "report_import"
    AI_SUMMARY = "ai_summary"
    MONTHLY_REVIEW = "monthly_review"
    OVERDUE_INVESTIGATION_SCAN = "overdue_investigation_scan"
    RETENTION_ENFORCEMENT_SCAN = "retention_enforcement_scan"
    REPORTING_MV_REFRESH = "reporting_mv_refresh"
    BATCH_DOCUMENT_LLM_SUMMARY = "batch_document_llm_summary"


class JobStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
