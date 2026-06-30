"""Sanitized Equifax 2026 layout corpus fixture (report_001).

Run from repository root::

    python tests/fixtures/credit_reports/equifax/2026/build_report_001.py

This writes ``report_001.pdf``. Regenerate ``report_001.expected.json`` via the
parser regression harness when parser output changes intentionally.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

REPORT_LINES: tuple[str, ...] = (
    "EQUIFAX",
    "Equifax Consumer Credit File",
    "Report Date: 07/10/2026",
    "",
    "CONSUMER INFORMATION",
    "Consumer: Morgan T. Lee",
    "DOB: 09/18/1988",
    "Social Security Number: 987-65-4321",
    "",
    "TRADELINES",
    "Tradeline 1",
    "Furnisher: Lakeside Credit Union",
    "Account Identifier: 99112233",
    "Portfolio Type: Installment",
    "Current Balance: $14,250.00",
    "High Credit: $18,000.00",
    "Account Status: Pays As Agreed",
    "Opened: 04/12/2020",
    "Last Reported: 07/01/2026",
    "",
    "Tradeline 2",
    "Furnisher: Summit Wireless",
    "Account Identifier: 00445566",
    "Portfolio Type: Revolving",
    "Current Balance: $210.75",
    "Account Status: 30 Days Past Due",
    "Opened: 11/03/2022",
    "Last Reported: 07/01/2026",
    "",
    "CREDIT INQUIRIES",
    "Inquiry 1",
    "Requested By: Auto Finance LLC",
    "Date of Inquiry: 05/22/2026",
    "Purpose: Hard",
    "",
    "PUBLIC RECORD INFORMATION",
    "Public Record 1",
    "Type: Civil Judgment",
    "Filed: 12/15/2020",
    "Status: Satisfied",
    "Amount: $2,400.00",
    "",
    "COLLECTION ACCOUNTS",
    "Collection Account 1",
    "Agency: Northstar Collections",
    "Original Creditor: Metro Medical Group",
    "Current Balance: $780.00",
    "Status: Disputed",
    "",
    "ACCOUNT SUMMARY",
    "Total Tradelines: 2",
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
