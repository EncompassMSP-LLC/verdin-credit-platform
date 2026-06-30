"""Unit tests for Experian layout detection and parsing."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from verdin_report_parsers import ParsedDocument
from verdin_report_parsers.constants import _MIN_PARSER_CONFIDENCE, Bureau
from verdin_report_parsers.parsers.experian.parser import ExperianParser
from verdin_report_parsers.parsers.fallback.parser import FallbackParser
from verdin_report_parsers.registry import select_parser

from tests.report_parsers.corpus import extract_pdf_text

_BUILD_SCRIPT = (
    Path(__file__).resolve().parents[4]
    / "tests"
    / "fixtures"
    / "credit_reports"
    / "experian"
    / "2026"
    / "build_report_001.py"
)


def _load_report_lines() -> tuple[str, ...]:
    spec = importlib.util.spec_from_file_location("build_report_001", _BUILD_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.REPORT_LINES


def _experian_document(text: str) -> ParsedDocument:
    return ParsedDocument(
        ocr_text=text,
        file_name="experian-report.pdf",
        title="Experian Consumer Credit Report",
        mime_type="application/pdf",
        document_type="credit_report",
        classification_confidence=0.95,
        document_id="doc-experian-001",
    )


def test_experian_can_parse_returns_zero_for_non_experian_report() -> None:
    parser = ExperianParser()
    document = ParsedDocument(
        ocr_text="EQUIFAX consumer credit report tradeline",
        file_name="equifax.pdf",
        title="Equifax Report",
        mime_type="application/pdf",
    )
    assert parser.can_parse(document) == 0.0


def test_experian_can_parse_requires_full_layout_signals() -> None:
    parser = ExperianParser()
    partial = _experian_document("Experian report for John Doe")
    full_text = "\n".join(_load_report_lines())
    full = _experian_document(full_text)

    assert parser.can_parse(partial) < 0.5
    assert parser.can_parse(full) >= 0.99


def test_registry_selects_experian_for_supported_layout() -> None:
    full_text = "\n".join(_load_report_lines())
    document = _experian_document(full_text)
    parser = select_parser(document)
    assert isinstance(parser, ExperianParser)
    assert not isinstance(parser, FallbackParser)


def test_registry_uses_fallback_for_non_experian_layout() -> None:
    parser = ExperianParser()
    document = ParsedDocument(
        ocr_text=(
            "EQUIFAX Consumer Credit Report\n"
            "PERSONAL INFORMATION\n"
            "Name: Alex M. Rivera\n"
            "ACCOUNTS\n"
            "Account 1\n"
            "Creditor: First Horizon Bank\n"
            "INQUIRIES\n"
            "PUBLIC RECORDS\n"
            "COLLECTIONS\n"
        ),
        file_name="equifax-report.pdf",
        title="Equifax Consumer Credit Report",
        mime_type="application/pdf",
        document_type="credit_report",
        classification_confidence=0.95,
    )

    assert parser.can_parse(document) < _MIN_PARSER_CONFIDENCE
    assert isinstance(select_parser(document), FallbackParser)


def test_experian_parse_populates_all_sections() -> None:
    parser = ExperianParser()
    full_text = "\n".join(_load_report_lines())
    report = parser.parse(_experian_document(full_text))

    assert report.bureau == Bureau.EXPERIAN
    assert report.consumer is not None
    assert report.consumer.name == "Alex M. Rivera"
    assert report.consumer.ssn_masked == "***-**-6789"
    assert len(report.accounts) == 2
    assert len(report.inquiries) == 2
    assert len(report.public_records) == 1
    assert len(report.collections) == 1
    assert report.summary is not None
    assert report.summary.total_accounts == 2
    assert report.summary.total_balance == 3780.25

    assert report.metadata is not None
    assert report.metadata.parser_name == "experian"
    assert report.metadata.is_partial is False
    assert report.metadata.field_confidence["parser.layout_confidence"] >= 0.99
    assert "layout.branding" in report.metadata.field_confidence


def test_experian_pdf_fixture_text_is_extractable() -> None:
    pdf_path = _BUILD_SCRIPT.parent / "report_001.pdf"
    if not pdf_path.is_file():
        pytest.skip("report_001.pdf not generated yet")

    text = extract_pdf_text(pdf_path.read_bytes())
    parser = ExperianParser()
    assert parser.can_parse(_experian_document(text)) >= 0.99
