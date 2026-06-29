"""Unit tests for document classification engine."""

from api.modules.documents.classification import ClassificationContext, classify_document
from api.modules.documents.classification.registry import list_classifiers
from api.modules.documents.constants import DocumentType


def test_registry_lists_all_classifiers() -> None:
    names = {classifier.name for classifier in list_classifiers()}
    assert "credit_report" in names
    assert "unknown" not in names


def test_classifies_credit_report_from_ocr_text() -> None:
    context = ClassificationContext(
        ocr_text="EQUIFAX consumer credit report tradeline account number",
        file_name="report.pdf",
        title="Bureau Pull",
        mime_type="application/pdf",
    )
    result = classify_document(context)
    assert result.document_type == DocumentType.CREDIT_REPORT
    assert result.confidence_score >= 0.5
    assert result.classifier_name == "credit_report"


def test_classifies_collection_letter() -> None:
    context = ClassificationContext(
        ocr_text="This is an attempt to collect a debt. Amount due immediately.",
        file_name="letter.pdf",
        title="Collector Notice",
        mime_type="application/pdf",
    )
    result = classify_document(context)
    assert result.document_type == DocumentType.COLLECTION_LETTER


def test_unknown_when_no_signals() -> None:
    context = ClassificationContext(
        ocr_text="lorem ipsum",
        file_name="notes.txt",
        title="Misc",
        mime_type="text/plain",
    )
    result = classify_document(context)
    assert result.document_type == DocumentType.UNKNOWN
    assert result.confidence_score <= 0.2
