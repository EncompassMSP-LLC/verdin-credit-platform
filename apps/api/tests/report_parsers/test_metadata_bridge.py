"""Tests for mapping parsed credit reports into flat metadata fields."""

from __future__ import annotations

import json
from pathlib import Path

from verdin_report_parsers.metadata_bridge import bridge_parsed_report_dict

FIXTURE_ROOT = (
    Path(__file__).resolve().parents[4]
    / "tests"
    / "fixtures"
    / "credit_reports"
    / "experian"
    / "2026"
)


def test_bridge_experian_expected_fixture() -> None:
    expected_path = FIXTURE_ROOT / "report_001.expected.json"
    report = json.loads(expected_path.read_text(encoding="utf-8"))

    bridged = bridge_parsed_report_dict(report)

    assert bridged.consumer_name == "Alex M. Rivera"
    assert bridged.bureau == "experian"
    assert bridged.creditor == "First Horizon Bank"
    assert bridged.account_number_masked == "****7890"
    assert bridged.balance == 3200.0
    assert bridged.extraction_method == "parser"
    assert bridged.confidence_score > 0
