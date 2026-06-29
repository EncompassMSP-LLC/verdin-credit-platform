"""Synthetic credit-report document used to drive the full pipeline.

The PDF is generated with embedded text so the worker's ``pypdf`` extractor
yields deterministic OCR text. The text is crafted so that:

* the rule-based classifier identifies it as a ``credit_report``;
* the metadata extractor finds creditor, bureau, account number, and dates;
* entity resolution matches it to the account created via ``ACCOUNT_PAYLOAD``.

Keeping the document content and the expected account in one place makes the
matching contract explicit and easy to maintain.
"""

from __future__ import annotations

from io import BytesIO

# --- Expected extracted values (asserted across the pipeline stages) ---------
EXPECTED_DOCUMENT_TYPE = "credit_report"
EXPECTED_BUREAU = "equifax"
EXPECTED_CREDITOR = "Example National Bank"
EXPECTED_ACCOUNT_MASKED = "****4521"
EXPECTED_ACCOUNT_LAST4 = "4521"
EXPECTED_REPORT_DATE = "2026-05-01"
EXPECTED_BALANCE = 2450.00

# --- Document body -----------------------------------------------------------
# Each entry is one rendered PDF line. Labels match the extractor's regexes.
CREDIT_REPORT_LINES: tuple[str, ...] = (
    "CONSUMER CREDIT REPORT",
    "Bureau: Equifax",
    "Consumer Name: Jordan A. Sample",
    "Date of Birth: 01/02/1985",
    "",
    "Tradelines",
    "Creditor: Example National Bank",
    "Account Number: ****4521",
    "Account Status: Open",
    "Payment Status: Late 60 Days",
    "Balance: $2,450.00",
    "Past Due: $420.00",
    "Date Opened: 03/15/2019",
    "Report Date: 05/01/2026",
    "",
    "This consumer credit report includes tradeline and account number data",
    "reported by Equifax for dispute review.",
)

# --- Case / account payloads sent to the API ---------------------------------
CASE_PAYLOAD = {
    "title": "E2E Lifecycle - Jordan Sample",
    "client_name": "Jordan A. Sample",
    "client_email": "jordan.sample@verdin-e2e.com",
    "priority": "high",
}

ACCOUNT_PAYLOAD = {
    "bureau": EXPECTED_BUREAU,
    "creditor_name": EXPECTED_CREDITOR,
    "original_creditor": EXPECTED_CREDITOR,
    "account_number_masked": EXPECTED_ACCOUNT_MASKED,
    "account_type": "credit_card",
    "account_status": "open",
    "payment_status": "late_60",
    "balance": EXPECTED_BALANCE,
    "past_due_amount": 420.00,
    "date_opened": "2019-03-15",
    "date_reported": "2026-05-01",
}

DOCUMENT_TITLE = "Equifax Credit Report - Jordan Sample"
DOCUMENT_FILENAME = "equifax-credit-report.pdf"
DOCUMENT_MIME_TYPE = "application/pdf"


def build_credit_report_pdf() -> bytes:
    """Render the credit-report lines into a real, text-extractable PDF."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    text_object = pdf.beginText(72, 720)
    text_object.setFont("Helvetica", 11)
    for line in CREDIT_REPORT_LINES:
        text_object.textLine(line)
    pdf.drawText(text_object)
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
