"""Import job modules so they self-register with the job registry."""

from worker.jobs import (
    ai_summary,
    batch_document_llm_summary,
    classify,
    credit_report_parse,
    entity_resolve,
    metadata_extract,
    monthly_review,
    ocr,
    overdue_investigation_scan,
    report_import,
    reporting_mv_refresh,
    retention_enforcement_scan,
    sms_marketing_campaign_delivery,
)

__all__ = [
    "ai_summary",
    "batch_document_llm_summary",
    "classify",
    "credit_report_parse",
    "entity_resolve",
    "metadata_extract",
    "monthly_review",
    "ocr",
    "overdue_investigation_scan",
    "report_import",
    "reporting_mv_refresh",
    "retention_enforcement_scan",
    "sms_marketing_campaign_delivery",
]
