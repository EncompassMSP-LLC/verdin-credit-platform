"""Experian parser regression suite — corpus fixtures must match expected output."""

from __future__ import annotations

import pytest
from verdin_report_parsers.parsers.experian.parser import ExperianParser

from tests.report_parsers.corpus import (
    assert_report_matches_expected,
    discover_experian_fixtures,
    load_expected_fixture,
    parse_fixture_pdf,
)


@pytest.fixture
def experian_parser() -> ExperianParser:
    return ExperianParser()


@pytest.mark.parametrize("pdf_path", discover_experian_fixtures(), ids=lambda path: path.stem)
def test_experian_corpus_regression(pdf_path, experian_parser: ExperianParser) -> None:
    """PDF → Parser → ParsedCreditReport must match version-controlled expected.json."""
    expected = load_expected_fixture(pdf_path)
    report = parse_fixture_pdf(pdf_path, parser=experian_parser)
    assert_report_matches_expected(report, expected)


def test_experian_corpus_has_fixtures() -> None:
    fixtures = discover_experian_fixtures()
    assert fixtures, "No Experian corpus PDF fixtures found under tests/fixtures/credit_reports/"
