"""IdentityIQ parser regression suite — corpus fixtures must match expected output."""

from __future__ import annotations

import pytest
from verdin_report_parsers.parsers.identityiq.parser import IdentityIQParser

from tests.report_parsers.corpus import (
    assert_report_matches_expected,
    discover_identityiq_fixtures,
    load_expected_fixture,
    parse_identityiq_fixture_pdf,
)


@pytest.fixture
def identityiq_parser() -> IdentityIQParser:
    return IdentityIQParser()


@pytest.mark.parametrize("pdf_path", discover_identityiq_fixtures(), ids=lambda path: path.stem)
def test_identityiq_corpus_regression(pdf_path, identityiq_parser: IdentityIQParser) -> None:
    """PDF → Parser → ParsedCreditReport must match version-controlled expected.json."""
    expected = load_expected_fixture(pdf_path)
    report = parse_identityiq_fixture_pdf(pdf_path, parser=identityiq_parser)
    assert_report_matches_expected(report, expected)


def test_identityiq_corpus_has_fixtures() -> None:
    fixtures = discover_identityiq_fixtures()
    assert fixtures, "No IdentityIQ corpus PDF fixtures found under tests/fixtures/credit_reports/"
