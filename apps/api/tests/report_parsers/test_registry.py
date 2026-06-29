"""Unit tests for the credit report parser registry."""

from verdin_report_parsers import ParsedDocument, parse_credit_report, select_parser
from verdin_report_parsers.parsers.fallback.parser import FallbackParser
from verdin_report_parsers.registry import list_bureau_parsers, list_parsers


def test_registry_lists_bureau_and_fallback_parsers() -> None:
    names = {parser.name for parser in list_parsers()}
    assert names == {"experian", "equifax", "transunion", "fallback"}


def test_bureau_parsers_not_selected_until_implemented() -> None:
    document = ParsedDocument(
        ocr_text="EQUIFAX consumer credit report tradeline",
        file_name="report.pdf",
        title="Bureau Pull",
        mime_type="application/pdf",
        document_type="credit_report",
        classification_confidence=0.9,
    )
    parser = select_parser(document)
    assert isinstance(parser, FallbackParser)


def test_parse_credit_report_uses_fallback_for_unknown_layout() -> None:
    document = ParsedDocument(
        ocr_text="lorem ipsum",
        file_name="unknown.pdf",
        title="Unknown",
        mime_type="application/pdf",
    )
    report = parse_credit_report(document)
    assert report.metadata is not None
    assert report.metadata.parser_name == "fallback"
    assert report.metadata.is_partial is True


def test_bureau_parser_stubs_are_registered() -> None:
    bureau_names = {parser.name for parser in list_bureau_parsers()}
    assert bureau_names == {"experian", "equifax", "transunion"}
