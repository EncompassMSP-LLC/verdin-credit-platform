"""Sanitized Experian 2026 layout corpus fixture (report_001).

Run from repository root::

    python tests/fixtures/credit_reports/experian/2026/build_report_001.py

This writes ``report_001.pdf``. Regenerate ``report_001.expected.json`` via the
parser regression harness when parser output changes intentionally.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

REPORT_LINES: tuple[str, ...] = (
    "EXPERIAN",
    "Experian Consumer Credit Report",
    "Report Date: 06/15/2026",
    "",
    "PERSONAL INFORMATION",
    "Name: Alex M. Rivera",
    "Date of Birth: 04/22/1990",
    "SSN: 123-45-6789",
    "",
    "ACCOUNTS",
    "Account 1",
    "Creditor: First Horizon Bank",
    "Account Number: ****7890",
    "Account Type: Revolving",
    "Balance: $3,200.00",
    "Credit Limit: $10,000.00",
    "Payment Status: Current",
    "Date Opened: 08/10/2018",
    "Date Reported: 06/01/2026",
    "",
    "Account 2",
    "Creditor: Metro Retail Card",
    "Account Number: ****3344",
    "Account Type: Revolving",
    "Balance: $580.25",
    "Payment Status: Late 30 Days",
    "Date Opened: 02/14/2021",
    "Date Reported: 06/01/2026",
    "",
    "INQUIRIES",
    "Inquiry 1",
    "Inquired By: Capital One",
    "Inquiry Date: 03/10/2026",
    "Inquiry Type: Hard",
    "",
    "Inquiry 2",
    "Inquired By: Chase Bank",
    "Inquiry Date: 01/05/2026",
    "Inquiry Type: Hard",
    "",
    "PUBLIC RECORDS",
    "Record 1",
    "Record Type: Tax Lien",
    "Filing Date: 11/20/2019",
    "Status: Released",
    "Amount: $1,200.00",
    "",
    "COLLECTIONS",
    "Collection 1",
    "Collection Agency: ABC Recovery Services",
    "Original Creditor: Utility Co",
    "Balance: $425.00",
    "Status: Open",
    "",
    "CREDIT SUMMARY",
    "Total Accounts: 2",
    "Total Inquiries: 2",
)

FIXTURE_DIR = Path(__file__).resolve().parent
PDF_PATH = FIXTURE_DIR / "report_001.pdf"


def build_pdf_bytes() -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    text_object = pdf.beginText(72, 720)
    text_object.setFont("Helvetica", 11)
    for line in REPORT_LINES:
        text_object.textLine(line)
    pdf.drawText(text_object)
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def write_pdf(path: Path = PDF_PATH) -> bytes:
    pdf_bytes = build_pdf_bytes()
    path.write_bytes(pdf_bytes)
    return pdf_bytes


if __name__ == "__main__":
    output = write_pdf()
    print(f"Wrote {PDF_PATH} ({len(output)} bytes)")
