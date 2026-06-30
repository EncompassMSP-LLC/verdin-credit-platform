"""TransUnion parser regression suite — corpus fixtures must match expected output."""

from __future__ import annotations

import pytest
from verdin_report_parsers.parsers.transunion.parser import TransUnionParser

from tests.report_parsers.corpus import (
    assert_report_matches_expected,
    discover_transunion_fixtures,
    load_expected_fixture,
    parse_transunion_fixture_pdf,
)


@pytest.fixture
def transunion_parser() -> TransUnionParser:
    return TransUnionParser()


@pytest.mark.parametrize("pdf_path", discover_transunion_fixtures(), ids=lambda path: path.stem)
def test_transunion_corpus_regression(pdf_path, transunion_parser: TransUnionParser) -> None:
    """PDF -> Parser -> ParsedCreditReport must match version-controlled expected.json."""
    expected = load_expected_fixture(pdf_path)
    report = parse_transunion_fixture_pdf(pdf_path, parser=transunion_parser)
    assert_report_matches_expected(report, expected)


def test_transunion_corpus_has_fixtures() -> None:
    fixtures = discover_transunion_fixtures()
    assert fixtures, "No TransUnion corpus PDF fixtures found under tests/fixtures/credit_reports/"
