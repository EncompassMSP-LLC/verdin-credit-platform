"""Tests for redacted credit report tradeline excerpts."""

from __future__ import annotations

from io import BytesIO

from api.modules.accounts.dispute_report_redaction import build_redacted_tradeline_excerpt


def _sample_report_pdf() -> bytes:
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter_page_size)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(72, 720, "Experian Credit Report")
    pdf.drawString(72, 680, "ACHIEVE PERSONAL LOANS")
    pdf.drawString(72, 660, "Account ****1081 Balance $18,764")
    pdf.drawString(72, 600, "CAPITAL ONE")
    pdf.drawString(72, 580, "Account ****5522 Balance $1,200")
    pdf.showPage()
    pdf.setFont("Helvetica", 12)
    pdf.drawString(72, 720, "Inquiries")
    pdf.save()
    return buffer.getvalue()


def test_build_redacted_tradeline_excerpt_keeps_target_page_only() -> None:
    excerpt = build_redacted_tradeline_excerpt(
        _sample_report_pdf(),
        target_creditor="ACHIEVE PERSONAL LOANS",
        target_account_masked="****1081",
        other_creditors=("CAPITAL ONE", "CHASE BANK"),
    )
    assert excerpt is not None
    assert excerpt.used_full_report_fallback is False
    assert excerpt.page_numbers == (1,)
    assert excerpt.redacted_creditor_count >= 1

    from pypdf import PdfReader

    reader = PdfReader(BytesIO(excerpt.pdf_bytes))
    text = reader.pages[0].extract_text() or ""
    assert "ACHIEVE PERSONAL LOANS" in text


def test_collect_redaction_rects_covers_to_page_bottom_after_next_account() -> None:
    """Split Experian-style page: target remnant on top, next account below."""
    from reportlab.lib.pagesizes import letter as letter_page_size
    from reportlab.pdfgen import canvas

    from api.modules.accounts.dispute_report_redaction import _collect_redaction_rects

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter_page_size)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(72, 740, "AMERICREDIT/GM FINANCIAL")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(72, 720, "Account 111833XXXX Status Paid")
    pdf.drawString(72, 400, "Annual Credit Report - Experian")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(72, 360, "TOTAL VISA BANK OF MISSOURI")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(72, 340, "Balance $489")
    pdf.drawString(72, 100, "PO BOX 1269 GREENVILLE SC")
    pdf.save()
    pdf_bytes = buffer.getvalue()

    import pdfplumber

    with pdfplumber.open(BytesIO(pdf_bytes)) as report:
        page = report.pages[0]
        rects = _collect_redaction_rects(
            page,
            other_creditors=("TOTAL VISA BANK OF MISSOURI", "CAPITAL ONE"),
            target_creditor="AMERICREDIT/GM FINANCIAL",
        )

    assert rects
    # Next-account band must reach near the page bottom (not a short 110pt pad).
    assert max(rect["bottom"] for rect in rects) >= float(page.height) - 10
    assert any(rect["bottom"] - rect["top"] > 200 for rect in rects)


def test_build_redacted_tradeline_excerpt_falls_back_when_target_missing() -> None:
    excerpt = build_redacted_tradeline_excerpt(
        _sample_report_pdf(),
        target_creditor="UNKNOWN LENDER",
        target_account_masked=None,
        other_creditors=("CAPITAL ONE",),
    )
    assert excerpt is not None
    assert excerpt.used_full_report_fallback is True
    assert excerpt.scanned_page_numbers == ()


def test_build_redacted_tradeline_excerpt_records_scanned_pages() -> None:
    excerpt = build_redacted_tradeline_excerpt(
        _sample_report_pdf(),
        target_creditor="ACHIEVE PERSONAL LOANS",
        target_account_masked="****1081",
        other_creditors=("CAPITAL ONE",),
    )
    assert excerpt is not None
    assert excerpt.used_full_report_fallback is False
    assert excerpt.scanned_page_numbers == (1,)


def test_build_redacted_tradeline_excerpt_uses_known_page_numbers() -> None:
    excerpt = build_redacted_tradeline_excerpt(
        _sample_report_pdf(),
        target_creditor="ACHIEVE PERSONAL LOANS",
        target_account_masked="****1081",
        other_creditors=("CAPITAL ONE",),
        known_page_numbers=(1,),
    )
    assert excerpt is not None
    assert excerpt.used_full_report_fallback is False
    assert excerpt.page_numbers == (1,)
    assert excerpt.scanned_page_numbers is None


def test_cluster_primary_pages_drops_distant_outliers() -> None:
    from api.modules.accounts.dispute_report_redaction import _cluster_primary_pages

    assert _cluster_primary_pages([9, 29]) == [9]
    assert _cluster_primary_pages([9, 10, 29]) == [9, 10]
    assert _cluster_primary_pages([3, 4, 5, 20]) == [3, 4, 5]


def test_build_redacted_tradeline_excerpt_known_empty_pages_falls_back() -> None:
    excerpt = build_redacted_tradeline_excerpt(
        _sample_report_pdf(),
        target_creditor="ACHIEVE PERSONAL LOANS",
        target_account_masked="****1081",
        other_creditors=("CAPITAL ONE",),
        known_page_numbers=(),
    )
    assert excerpt is not None
    assert excerpt.used_full_report_fallback is True
    assert excerpt.scanned_page_numbers is None
