"""Unit tests for TransUnion layout detection and parsing."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from verdin_report_parsers import ParsedDocument
from verdin_report_parsers.constants import _MIN_PARSER_CONFIDENCE, Bureau
from verdin_report_parsers.parsers.equifax.parser import EquifaxParser
from verdin_report_parsers.parsers.fallback.parser import FallbackParser
from verdin_report_parsers.parsers.transunion.parser import TransUnionParser
from verdin_report_parsers.registry import select_parser

from tests.report_parsers.corpus import extract_pdf_text

_BUILD_SCRIPT = (
    Path(__file__).resolve().parents[4]
    / "tests"
    / "fixtures"
    / "credit_reports"
    / "transunion"
    / "2026"
    / "build_report_001.py"
)


def _load_report_lines() -> tuple[str, ...]:
    spec = importlib.util.spec_from_file_location("build_report_001", _BUILD_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.REPORT_LINES


def _transunion_document(text: str) -> ParsedDocument:
    return ParsedDocument(
        ocr_text=text,
        file_name="transunion-report.pdf",
        title="TransUnion Consumer Credit Report",
        mime_type="application/pdf",
        document_type="credit_report",
        classification_confidence=0.95,
        document_id="doc-transunion-001",
    )


def test_transunion_can_parse_returns_zero_for_non_transunion_report() -> None:
    parser = TransUnionParser()
    document = ParsedDocument(
        ocr_text="EQUIFAX consumer credit file tradelines",
        file_name="equifax.pdf",
        title="Equifax Report",
        mime_type="application/pdf",
    )
    assert parser.can_parse(document) == 0.0


def test_transunion_can_parse_requires_full_layout_signals() -> None:
    parser = TransUnionParser()
    partial = _transunion_document("TransUnion report for Avery Morgan")
    full_text = "\n".join(_load_report_lines())
    full = _transunion_document(full_text)

    assert parser.can_parse(partial) < _MIN_PARSER_CONFIDENCE
    assert parser.can_parse(full) >= 0.99


def test_registry_selects_transunion_for_supported_layout() -> None:
    full_text = "\n".join(_load_report_lines())
    document = _transunion_document(full_text)
    parser = select_parser(document)
    assert isinstance(parser, TransUnionParser)
    assert not isinstance(parser, FallbackParser)


def test_registry_does_not_select_transunion_for_equifax_layout() -> None:
    parser = TransUnionParser()
    document = ParsedDocument(
        ocr_text=(
            "EQUIFAX Consumer Credit File\n"
            "CONSUMER INFORMATION\n"
            "Consumer: Avery J. Morgan\n"
            "TRADELINES\n"
            "Tradeline 1\n"
            "Furnisher: Summit Retail Bank\n"
            "CREDIT INQUIRIES\n"
            "PUBLIC RECORD INFORMATION\n"
            "COLLECTION ACCOUNTS\n"
        ),
        file_name="equifax-report.pdf",
        title="Equifax Consumer Credit File",
        mime_type="application/pdf",
        document_type="credit_report",
        classification_confidence=0.95,
    )

    assert parser.can_parse(document) < _MIN_PARSER_CONFIDENCE
    assert isinstance(select_parser(document), EquifaxParser)


def test_registry_prefers_transunion_over_equifax_for_transunion_layout() -> None:
    full_text = "\n".join(_load_report_lines())
    document = _transunion_document(full_text)
    assert isinstance(select_parser(document), TransUnionParser)
    assert EquifaxParser().can_parse(document) < _MIN_PARSER_CONFIDENCE


def test_transunion_parse_populates_all_sections() -> None:
    parser = TransUnionParser()
    full_text = "\n".join(_load_report_lines())
    report = parser.parse(_transunion_document(full_text))

    assert report.bureau == Bureau.TRANSUNION
    assert report.consumer is not None
    assert report.consumer.name == "Avery J. Morgan"
    assert report.consumer.ssn_masked == "***-**-9012"
    assert len(report.accounts) == 2
    assert len(report.inquiries) == 1
    assert len(report.public_records) == 1
    assert len(report.collections) == 1
    assert report.summary is not None
    assert report.summary.total_accounts == 2
    assert report.summary.total_balance == 11295.5

    assert report.metadata is not None
    assert report.metadata.parser_name == "transunion"
    assert report.metadata.is_partial is False
    assert report.metadata.field_confidence["parser.layout_confidence"] >= 0.99
    assert "layout.branding" in report.metadata.field_confidence


def test_transunion_pdf_fixture_text_is_extractable() -> None:
    pdf_path = _BUILD_SCRIPT.parent / "report_001.pdf"
    if not pdf_path.is_file():
        pytest.skip("report_001.pdf not generated yet")

    text = extract_pdf_text(pdf_path.read_bytes())
    parser = TransUnionParser()
    assert parser.can_parse(_transunion_document(text)) >= 0.99


_INTERACTIVE_SAMPLE = """
Credit Report
My VantageScore 3.0
605
FAIR
Credit Profile Summary
Credit Report Date
07/26/2026
Credit Score
605
Personal Information
Name
JANE SAMPLE
Date of Birth
01/15/1990
Current Address
ATLANTA GA 30301
Inquiries
SAMPLE AUTO
02/25/2026
Accounts
Revolving
Account Name Balance Balance Date Monthly Term
Payment
SAMPLEBANK $0 09/01/2020 $0 0
Account Details
Account Number
539176127109****
Condition
Derogatory
Responsibility
Individual
Current Balance
$0
Original Balance
$420
Limit
$240
Monthly Payment
$0
Last Payment
01/18/2020
Status
Collection / Charge-Off
Loan Term
0
Loan Type
Charge account
Opened
09/20/2019
Reported
11/01/2020
Remarks
Charged off as bad debt|Purchased by another lender
Creditor Information
COMENITY BANK/VCTRSSEC PO BOX 182789
COLUMBUS,OH 43218
Payment Status
Payment Status
Past Due Amount
Late Payments
30 Days - 0
Installment
Account Name Balance Balance Date Monthly Term
Payment
BRIDGECREST $21,343 04/30/2026 $0 69
Account Details
Account Number
20016626****
Condition
Derogatory
Responsibility
Joint
Current Balance
$21,343
Original Balance
$26,726
Limit
$0
Monthly Payment
$0
Last Payment
05/12/2026
Status
Loan Term
69
Loan Type
Auto Loan
Opened
01/02/2023
Reported
06/30/2026
Remarks
Voluntary repossession|Returned voluntarily
Creditor Information
BRIDGECREST PO BOX 29018 PHOENIX,AZ 85038
Phone#: 8008433825
Payment Status
Payment Status
Collections
Account Name Balance Balance Date Monthly Term
Payment
MIDLAND CRED $420 07/23/2026
Account Details
Account Number
30767****
Condition
Derogatory
Responsibility
Individual
Current Balance
$420
Original Balance
$420
Limit
Monthly Payment
Last Payment
Status
Collection / Charge-Off
Loan Term
Loan Type
Opened
09/29/2020
Reported
07/23/2026
Remarks
Account information disputed by consumer, meets
FCRA requirements
Creditor Information
MIDLAND CREDIT MANAGEMEN 350 CAMINO DE LA
REINA SAN DIEGO,CA 92108 Phone#: 8778220381
Payment Status
Payment Status
Other
Account Name Balance Balance Date Monthly Term
Payment
CHIME-STRIDE $0 01/11/2024 $0 0
Account Details
Account Number
66813249****
Condition
Open
Responsibility
Individual
Current Balance
$0
Original Balance
$39
Limit
$0
Monthly Payment
$0
Last Payment
01/11/2024
Status
OK
Loan Term
0
Loan Type
Secured credit card
Opened
12/07/2023
Reported
06/02/2026
Remarks
Creditor Information
CHIME - STRIDE BANK PO BOX 417 SAN
FRANCISCO,CA 94104 Phone#: 8442446363
Payment Status
Payment Status
Public Records
© 2026 TransUnion Interactive, Inc. | All Rights Reserved
"""


def test_transunion_interactive_layout_extracts_tradelines_and_report_date() -> None:
    parser = TransUnionParser()
    report = parser.parse(_transunion_document(_INTERACTIVE_SAMPLE))

    assert report.bureau == Bureau.TRANSUNION
    assert report.consumer is not None
    assert report.consumer.name == "JANE SAMPLE"
    assert len(report.accounts) == 4
    creditors = {account.creditor_name for account in report.accounts}
    assert "COMENITY BANK/VCTRSSEC" in creditors
    assert "BRIDGECREST" in creditors
    assert "MIDLAND CREDIT MANAGEMEN" in creditors
    assert "CHIME - STRIDE BANK" in creditors

    midland = next(a for a in report.accounts if a.creditor_name == "MIDLAND CREDIT MANAGEMEN")
    assert midland.balance == 420.0
    assert midland.account_status == "Collection / Charge-Off"
    assert midland.account_number_masked == "****0767"

    assert "no_tradelines_extracted" not in report.metadata.warnings
    assert "report_date_missing" not in report.metadata.warnings
    assert report.metadata.field_confidence.get("report.report_date") == 0.91
    assert report.metadata.is_partial is False


def test_transunion_interactive_report_date_survives_ocr_flattening() -> None:
    from verdin_report_parsers.parsers.transunion.extract import extract_report_date

    flat = "Credit Report Date 07/26/2026 Credit Score 605"
    report_date, confidence = extract_report_date(flat)
    assert report_date == "07/26/2026"
    assert confidence["report.report_date"] == 0.91
