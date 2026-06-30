"""Unit tests for Equifax layout detection and parsing."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from verdin_report_parsers import ParsedDocument
from verdin_report_parsers.constants import _MIN_PARSER_CONFIDENCE, Bureau
from verdin_report_parsers.parsers.equifax.parser import EquifaxParser
from verdin_report_parsers.parsers.fallback.parser import FallbackParser
from verdin_report_parsers.registry import select_parser

from tests.report_parsers.corpus import extract_pdf_text

_BUILD_SCRIPT = (
    Path(__file__).resolve().parents[4]
    / "tests"
    / "fixtures"
    / "credit_reports"
    / "equifax"
    / "2026"
    / "build_report_001.py"
)


def _load_report_lines() -> tuple[str, ...]:
    spec = importlib.util.spec_from_file_location("build_report_001", _BUILD_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.REPORT_LINES


def _equifax_document(text: str) -> ParsedDocument:
    return ParsedDocument(
        ocr_text=text,
        file_name="equifax-report.pdf",
        title="Equifax Consumer Credit File",
        mime_type="application/pdf",
        document_type="credit_report",
        classification_confidence=0.95,
        document_id="doc-equifax-001",
    )


def test_equifax_can_parse_returns_zero_for_non_equifax_report() -> None:
    parser = EquifaxParser()
    document = ParsedDocument(
        ocr_text="EXPERIAN consumer credit report tradeline",
        file_name="experian.pdf",
        title="Experian Report",
        mime_type="application/pdf",
    )
    assert parser.can_parse(document) == 0.0


def test_equifax_can_parse_requires_full_layout_signals() -> None:
    parser = EquifaxParser()
    partial = _equifax_document("Equifax report for Morgan Lee")
    full_text = "\n".join(_load_report_lines())
    full = _equifax_document(full_text)

    assert parser.can_parse(partial) < _MIN_PARSER_CONFIDENCE
    assert parser.can_parse(full) >= 0.99


def test_registry_selects_equifax_for_supported_layout() -> None:
    full_text = "\n".join(_load_report_lines())
    document = _equifax_document(full_text)
    parser = select_parser(document)
    assert isinstance(parser, EquifaxParser)
    assert not isinstance(parser, FallbackParser)


def test_registry_uses_fallback_for_non_equifax_layout() -> None:
    parser = EquifaxParser()
    document = ParsedDocument(
        ocr_text=(
            "TRANSUNION Consumer Disclosure\n"
            "CONSUMER INFORMATION\n"
            "Name: Morgan T. Lee\n"
            "TRADELINES\n"
            "Tradeline 1\n"
            "Furnisher: Lakeside Credit Union\n"
            "CREDIT INQUIRIES\n"
            "PUBLIC RECORD INFORMATION\n"
            "COLLECTION ACCOUNTS\n"
        ),
        file_name="transunion-report.pdf",
        title="TransUnion Consumer Disclosure",
        mime_type="application/pdf",
        document_type="credit_report",
        classification_confidence=0.95,
    )

    assert parser.can_parse(document) < _MIN_PARSER_CONFIDENCE
    assert isinstance(select_parser(document), FallbackParser)


def test_equifax_parse_populates_all_sections() -> None:
    parser = EquifaxParser()
    full_text = "\n".join(_load_report_lines())
    report = parser.parse(_equifax_document(full_text))

    assert report.bureau == Bureau.EQUIFAX
    assert report.consumer is not None
    assert report.consumer.name == "Morgan T. Lee"
    assert report.consumer.ssn_masked == "***-**-4321"
    assert len(report.accounts) == 2
    assert len(report.inquiries) == 1
    assert len(report.public_records) == 1
    assert len(report.collections) == 1
    assert report.summary is not None
    assert report.summary.total_accounts == 2
    assert report.summary.total_balance == 14460.75

    assert report.metadata is not None
    assert report.metadata.parser_name == "equifax"
    assert report.metadata.is_partial is False
    assert report.metadata.field_confidence["parser.layout_confidence"] >= 0.99
    assert "layout.branding" in report.metadata.field_confidence


def test_equifax_pdf_fixture_text_is_extractable() -> None:
    pdf_path = _BUILD_SCRIPT.parent / "report_001.pdf"
    if not pdf_path.is_file():
        pytest.skip("report_001.pdf not generated yet")

    text = extract_pdf_text(pdf_path.read_bytes())
    parser = EquifaxParser()
    assert parser.can_parse(_equifax_document(text)) >= 0.99
