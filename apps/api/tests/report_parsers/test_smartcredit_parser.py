"""Unit tests for SmartCredit layout detection and parsing."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from verdin_report_parsers import ParsedDocument
from verdin_report_parsers.constants import Bureau
from verdin_report_parsers.parsers.experian.parser import ExperianParser
from verdin_report_parsers.parsers.fallback.parser import FallbackParser
from verdin_report_parsers.parsers.identityiq.parser import IdentityIQParser
from verdin_report_parsers.parsers.smartcredit.parser import SmartCreditParser
from verdin_report_parsers.registry import select_parser

_BUILD_SCRIPT = (
    Path(__file__).resolve().parents[4]
    / "tests"
    / "fixtures"
    / "credit_reports"
    / "smartcredit"
    / "2026"
    / "build_report_001.py"
)


def _load_report_lines() -> tuple[str, ...]:
    spec = importlib.util.spec_from_file_location("build_smartcredit_report_001", _BUILD_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.REPORT_LINES


def _smartcredit_document(text: str) -> ParsedDocument:
    return ParsedDocument(
        ocr_text=text,
        file_name="smartcredit-report.pdf",
        title="Credit Report - SmartCredit",
        mime_type="application/pdf",
        document_type="credit_report",
        classification_confidence=0.95,
        document_id="doc-smartcredit-001",
    )


def test_smartcredit_can_parse_returns_zero_for_non_smartcredit_report() -> None:
    parser = SmartCreditParser()
    document = ParsedDocument(
        ocr_text="Experian Consumer Credit Report tradeline",
        file_name="experian.pdf",
        title="Experian Report",
        mime_type="application/pdf",
    )
    assert parser.can_parse(document) == 0.0


def test_smartcredit_can_parse_returns_zero_for_identityiq_report() -> None:
    parser = SmartCreditParser()
    document = ParsedDocument(
        ocr_text="Credit Report - IdentityIQ\nhttps://member.identityiq.com/CreditReport.aspx",
        file_name="identityiq.pdf",
        title="Credit Report - IdentityIQ",
        mime_type="application/pdf",
    )
    assert parser.can_parse(document) == 0.0
    assert IdentityIQParser().can_parse(document) > 0.0


def test_smartcredit_can_parse_scores_full_layout_high() -> None:
    parser = SmartCreditParser()
    full_text = "\n".join(_load_report_lines())
    assert parser.can_parse(_smartcredit_document(full_text)) >= 0.9


def test_registry_selects_smartcredit_over_bureau_parsers() -> None:
    full_text = "\n".join(_load_report_lines())
    document = _smartcredit_document(full_text)
    parser = select_parser(document)
    assert isinstance(parser, SmartCreditParser)
    assert not isinstance(parser, ExperianParser)
    assert not isinstance(parser, FallbackParser)
    assert ExperianParser().can_parse(document) == 0.0
    assert IdentityIQParser().can_parse(document) == 0.0


def test_smartcredit_parse_expands_tri_bureau_accounts() -> None:
    parser = SmartCreditParser()
    full_text = "\n".join(_load_report_lines())
    report = parser.parse(_smartcredit_document(full_text))

    assert report.bureau == Bureau.UNKNOWN
    assert report.consumer is not None
    assert report.consumer.name == "Jordan K. Ellis"
    assert report.consumer.ssn_masked == "***-**-4421"

    # First account on all 3 bureaus + second account on TU/EX only = 5 tradelines
    assert len(report.accounts) == 5
    first_horizon = [a for a in report.accounts if a.creditor_name == "First Horizon Bank"]
    assert len(first_horizon) == 3
    assert {a.bureau for a in first_horizon} == {"transunion", "experian", "equifax"}
    assert all(a.account_number_masked == "****7890" for a in first_horizon)

    metro = [a for a in report.accounts if a.creditor_name == "Metro Retail Card"]
    assert len(metro) == 2
    assert {a.bureau for a in metro} == {"transunion", "experian"}

    assert len(report.inquiries) == 2
    assert len(report.public_records) == 1
    assert len(report.collections) == 1
    assert report.summary is not None
    assert report.summary.total_accounts == 5
    assert report.metadata is not None
    assert report.metadata.parser_name == "smartcredit"
    assert report.metadata.is_partial is False
