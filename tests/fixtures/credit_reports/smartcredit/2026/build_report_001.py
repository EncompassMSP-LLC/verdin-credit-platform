"""Sanitized SmartCredit 2026 tri-merge layout corpus fixture (report_001).

Run from repository root::

    python tests/fixtures/credit_reports/smartcredit/2026/build_report_001.py
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

REPORT_LINES: tuple[str, ...] = (
    "Credit Report - SmartCredit",
    "https://www.smartcredit.com/member/credit-report",
    "Report Date: 06/15/2026",
    "",
    "Personal Information",
    "Name: Jordan K. Ellis",
    "Date of Birth: 09/03/1988",
    "SSN: XXX-XX-4421",
    "",
    "Credit Summary",
    "Total Accounts: 2",
    "",
    "Accounts",
    "Account Name: First Horizon Bank",
    "Account Number: ****7890",
    "Account Type: Revolving",
    "TransUnion Experian Equifax",
    "Balance $3200.00 $3200.00 $3250.00",
    "Credit Limit $10000.00 $10000.00 $10000.00",
    "Account Status Open Open Open",
    "Payment Status Current Current Current",
    "Date Opened 08/10/2018 08/10/2018 08/10/2018",
    "Date Reported 06/01/2026 06/01/2026 06/01/2026",
    "",
    "Account Name: Metro Retail Card",
    "Account Number: ****3344",
    "Account Type: Revolving",
    "TransUnion Experian Equifax",
    "Balance $580.25 $580.25 --",
    "Credit Limit $2500.00 $2500.00 --",
    "Account Status Open Open --",
    "Payment Status Late 30 Late 30 --",
    "Date Opened 02/14/2021 02/14/2021 --",
    "Date Reported 06/01/2026 06/01/2026 --",
    "",
    "Inquiries",
    "Inquiry 1",
    "Inquired By: Capital One",
    "Inquiry Date: 03/10/2026",
    "Inquiry Type: Hard",
    "Bureau: Experian",
    "",
    "Inquiry 2",
    "Inquired By: Chase Bank",
    "Inquiry Date: 01/05/2026",
    "Inquiry Type: Hard",
    "Bureau: Equifax",
    "",
    "Public Records",
    "Record 1",
    "Record Type: Tax Lien",
    "Filing Date: 11/20/2019",
    "Status: Released",
    "Amount: $1,200.00",
    "",
    "Collections",
    "Collection 1",
    "Collection Agency: ABC Recovery Services",
    "Original Creditor: Utility Co",
    "Balance: $425.00",
    "Status: Open",
)

FIXTURE_DIR = Path(__file__).resolve().parent
PDF_PATH = FIXTURE_DIR / "report_001.pdf"


def build_pdf_bytes() -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen.canvas import Canvas

    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=letter)
    y = 750
    for line in REPORT_LINES:
        canvas.drawString(40, y, line)
        y -= 14
        if y < 40:
            canvas.showPage()
            y = 750
    canvas.save()
    return buffer.getvalue()


def main() -> None:
    PDF_PATH.write_bytes(build_pdf_bytes())
    print(f"Wrote {PDF_PATH}")


if __name__ == "__main__":
    main()
