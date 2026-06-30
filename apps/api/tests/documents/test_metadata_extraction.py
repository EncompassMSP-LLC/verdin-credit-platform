"""Unit tests for rule-based metadata extraction."""

from verdin_document_metadata import ExtractionContext, extract_metadata

SAMPLE_CREDIT_REPORT_TEXT = """
Consumer Name: Doc Client
Creditor: Example Bank
Bureau: Equifax
Account #: xxxx1234
Balance: $1,500.00
Report Date: 01/15/2026
Payment Status: Late 60
Address: 123 Main St Springfield IL
Phone: (555) 123-4567
"""


def test_extract_metadata_fields() -> None:
    result = extract_metadata(
        ExtractionContext(
            ocr_text=SAMPLE_CREDIT_REPORT_TEXT,
            file_name="equifax_report.pdf",
            title="Equifax Pull",
            document_type="credit_report",
        )
    )
    assert result.consumer_name == "Doc Client"
    assert result.bureau == "equifax"
    assert result.creditor == "Example Bank"
    assert result.account_number_masked == "****1234"
    assert result.balance == 1500.0
    assert result.report_date == "2026-01-15"
    assert result.payment_status == "Late 60"
    assert len(result.addresses) >= 1
    assert "(555) 123-4567" in result.phone_numbers
    assert result.confidence_score > 0


def test_extract_metadata_empty_text() -> None:
    result = extract_metadata(
        ExtractionContext(ocr_text=None, file_name="empty.pdf", title="Empty", document_type=None)
    )
    assert result.confidence_score == 0.0
    assert result.consumer_name is None
