"""Equifax parser regression suite — corpus fixtures must match expected output."""

from __future__ import annotations

import pytest
from verdin_report_parsers.parsers.equifax.parser import EquifaxParser

from tests.report_parsers.corpus import (
    assert_report_matches_expected,
    discover_equifax_fixtures,
    load_expected_fixture,
    parse_equifax_fixture_pdf,
)


@pytest.fixture
def equifax_parser() -> EquifaxParser:
    return EquifaxParser()


@pytest.mark.parametrize("pdf_path", discover_equifax_fixtures(), ids=lambda path: path.stem)
def test_equifax_corpus_regression(pdf_path, equifax_parser: EquifaxParser) -> None:
    """PDF -> Parser -> ParsedCreditReport must match version-controlled expected.json."""
    expected = load_expected_fixture(pdf_path)
    report = parse_equifax_fixture_pdf(pdf_path, parser=equifax_parser)
    assert_report_matches_expected(report, expected)


def test_equifax_corpus_has_fixtures() -> None:
    fixtures = discover_equifax_fixtures()
    assert fixtures, "No Equifax corpus PDF fixtures found under tests/fixtures/credit_reports/"
