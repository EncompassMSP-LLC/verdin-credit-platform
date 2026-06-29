"""Import job modules so they self-register with the job registry."""

from worker.jobs import ai_summary, classify, monthly_review, ocr, report_import

__all__ = [
    "ai_summary",
    "classify",
    "monthly_review",
    "ocr",
    "report_import",
]
