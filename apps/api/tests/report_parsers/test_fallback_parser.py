"""Unit tests for the fallback credit report parser."""

from verdin_report_parsers import ParsedDocument
from verdin_report_parsers.constants import Bureau
from verdin_report_parsers.parsers.fallback.parser import FallbackParser


def test_fallback_always_eligible() -> None:
    parser = FallbackParser()
    document = ParsedDocument(
        ocr_text=None,
        file_name="empty.pdf",
        title="Empty",
        mime_type="application/pdf",
    )
    assert parser.can_parse(document) > 0.0


def test_fallback_never_raises_on_empty_document() -> None:
    parser = FallbackParser()
    document = ParsedDocument(
        ocr_text="",
        file_name="empty.pdf",
        title="Empty",
        mime_type="application/pdf",
        document_type="credit_report",
        classification_confidence=0.8,
        document_id="doc-123",
    )
    report = parser.parse(document)
    assert report.report_id == "doc-123"
    assert report.metadata is not None
    assert report.metadata.parser_name == "fallback"
    assert report.metadata.is_partial is True
    assert "minimal_extraction" in report.metadata.warnings


def test_fallback_extracts_partial_equifax_report() -> None:
    parser = FallbackParser()
    document = ParsedDocument(
        ocr_text=(
            "EQUIFAX consumer credit report\n"
            "Consumer Name: Jane Q Public\n"
            "Creditor: Example Bank\n"
            "Account #: XXXX1234\n"
            "Balance: $1,250.50\n"
            "Payment Status: Current\n"
            "Date Opened: 01/15/2020"
        ),
        file_name="equifax-pull.pdf",
        title="Equifax Report",
        mime_type="application/pdf",
        document_type="credit_report",
        classification_confidence=0.9,
    )
    report = parser.parse(document)
    assert report.bureau == Bureau.EQUIFAX
    assert report.consumer is not None
    assert report.consumer.name == "Jane Q Public"
    assert len(report.accounts) == 1
    assert report.accounts[0].creditor_name == "Example Bank"
    assert report.accounts[0].account_number_masked == "****1234"
    assert report.accounts[0].balance == 1250.5
    assert report.summary is not None
    assert report.summary.total_accounts == 1
    assert report.metadata is not None
    assert report.metadata.field_confidence["consumer.name"] > 0


def test_fallback_masks_ssn_when_present() -> None:
    parser = FallbackParser()
    document = ParsedDocument(
        ocr_text="Experian report for John Doe 123-45-6789",
        file_name="report.pdf",
        title="Report",
        mime_type="application/pdf",
    )
    report = parser.parse(document)
    assert report.bureau == Bureau.EXPERIAN
    assert report.consumer is not None
    assert report.consumer.ssn_masked == "***-**-6789"
