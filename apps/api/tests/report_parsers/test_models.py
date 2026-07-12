"""Unit tests for parsed credit report models."""

from verdin_report_parsers import (
    PARSED_CREDIT_REPORT_SCHEMA_VERSION,
    ConsumerInfo,
    ParsedCreditReport,
    ParseMetadata,
    TradelineAccount,
)
from verdin_report_parsers.constants import Bureau


def test_parsed_credit_report_has_versioned_schema() -> None:
    report = ParsedCreditReport(
        bureau=Bureau.EQUIFAX,
        metadata=ParseMetadata.now(parser_name="fallback"),
    )
    assert report.schema_version == PARSED_CREDIT_REPORT_SCHEMA_VERSION
    assert report.schema_version == "1.1"


def test_parsed_credit_report_serializes_to_dict() -> None:
    report = ParsedCreditReport(
        bureau=Bureau.EXPERIAN,
        consumer=ConsumerInfo(name="Jane Doe", confidence=0.6),
        accounts=(
            TradelineAccount(
                creditor_name="Example Bank",
                account_number_masked="****1234",
                balance=250.0,
                confidence=0.5,
            ),
        ),
        metadata=ParseMetadata.now(parser_name="fallback", is_partial=True),
    )
    payload = report.as_dict()
    assert payload["schema_version"] == "1.1"
    assert payload["bureau"] == "experian"
    assert payload["consumer"]["name"] == "Jane Doe"
    assert payload["accounts"][0]["creditor_name"] == "Example Bank"
    assert payload["metadata"]["is_partial"] is True
