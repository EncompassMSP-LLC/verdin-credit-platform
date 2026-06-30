"""Sanitized TransUnion 2026 layout corpus fixture (report_001).

Run from repository root::

    python tests/fixtures/credit_reports/transunion/2026/build_report_001.py

This writes ``report_001.pdf``. Regenerate ``report_001.expected.json`` via the
parser regression harness when parser output changes intentionally.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

REPORT_LINES: tuple[str, ...] = (
    "TRANSUNION",
    "TransUnion Consumer Credit Report",
    "Report Date: 08/15/2026",
    "",
    "PERSONAL INFORMATION",
    "Name: Avery J. Morgan",
    "Date of Birth: 05/12/1987",
    "Social Security Number: 456-78-9012",
    "",
    "ACCOUNTS",
    "Account 1",
    "Subscriber: Summit Retail Bank",
    "Account Number: 7788990011223344",
    "Account Type: Revolving",
    "Balance: $1,875.50",
    "High Credit: $4,500.00",
    "Account Status: Late 30 Days",
    "Date Opened: 04/18/2018",
    "Date Updated: 08/01/2026",
    "",
    "Account 2",
    "Subscriber: Metro Auto Finance",
    "Account Number: 5566778899001122",
    "Account Type: Installment",
    "Balance: $9,420.00",
    "High Credit: $18,000.00",
    "Account Status: Current",
    "Date Opened: 09/22/2020",
    "Date Updated: 08/01/2026",
    "",
    "INQUIRIES",
    "Inquiry 1",
    "Inquired By: Capital One",
    "Inquiry Date: 06/12/2026",
    "Inquiry Type: Hard",
    "",
    "PUBLIC RECORDS",
    "Public Record 1",
    "Record Type: Civil Judgment",
    "Filed: 10/05/2019",
    "Status: Satisfied",
    "Amount: $1,800.00",
    "",
    "COLLECTIONS",
    "Collection 1",
    "Agency: Northstar Recovery",
    "Original Creditor: Utility Services",
    "Balance: $640.00",
    "Status: Open",
    "",
    "CREDIT SUMMARY",
    "Total Accounts: 2",
    "Total Inquiries: 1",
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
