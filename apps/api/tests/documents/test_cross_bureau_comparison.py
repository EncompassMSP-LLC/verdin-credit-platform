"""Unit tests for cross-bureau tradeline comparison."""

from __future__ import annotations

import uuid

from api.modules.documents.cross_bureau_comparison import (
    compare_cross_bureau_reports,
    tradeline_match_key,
)


def test_tradeline_match_key_uses_creditor_and_last_four() -> None:
    assert tradeline_match_key("ACHIEVE PERSONAL LOANS", "APP1081****") == tradeline_match_key(
        "Achieve Personal Loans LLC",
        "****1081",
    )


def test_compare_cross_bureau_reports_detects_balance_and_missing_bureaus() -> None:
    case_id = uuid.uuid4()
    experian_doc = uuid.uuid4()
    equifax_doc = uuid.uuid4()
    transunion_doc = uuid.uuid4()

    result = compare_cross_bureau_reports(
        case_id=case_id,
        reports_by_bureau={
            "experian": (
                experian_doc,
                {
                    "accounts": [
                        {
                            "creditor_name": "ACHIEVE PERSONAL LOANS",
                            "account_number_masked": "APP1081****",
                            "balance": 18764.0,
                            "payment_status": "Account charged off",
                        }
                    ]
                },
            ),
            "equifax": (
                equifax_doc,
                {
                    "accounts": [
                        {
                            "creditor_name": "ACHIEVE PERSONAL LOANS",
                            "account_number_masked": "****1081",
                            "balance": 18000.0,
                            "payment_status": "Collection account",
                        }
                    ]
                },
            ),
            "transunion": (
                transunion_doc,
                {
                    "accounts": [
                        {
                            "creditor_name": "ACHIEVE PERSONAL LOANS",
                            "account_number_masked": "APP1081****",
                            "balance": 18764.0,
                            "payment_status": "Charge-off",
                        }
                    ]
                },
            ),
        },
    )

    achieve = next(
        item for item in result.discrepancies if item.creditor_name == "ACHIEVE PERSONAL LOANS"
    )
    assert achieve.dispute_ready is True
    assert achieve.requires_investigation is False
    assert achieve.workflow_tier == "dispute"
    assert achieve.classification == "reporting_inconsistency"
    assert "balance_mismatch" in achieve.discrepancy_types
    assert "status_mismatch" in achieve.discrepancy_types
    assert achieve.confidence_score >= 70
    assert result.summary["dispute_ready"] >= 1
    assert achieve.field_diffs
    assert any("balance" in diff.field for diff in achieve.field_diffs)


def test_compare_cross_bureau_reports_detects_past_due_and_dofd_mismatches() -> None:
    case_id = uuid.uuid4()
    result = compare_cross_bureau_reports(
        case_id=case_id,
        reports_by_bureau={
            "experian": (
                uuid.uuid4(),
                {
                    "accounts": [
                        {
                            "creditor_name": "Capital One",
                            "account_number_masked": "****4242",
                            "balance": 4213.0,
                            "past_due_amount": 4213.0,
                            "payment_status": "Charge Off",
                            "date_first_delinquency": "01/15/2020",
                        }
                    ]
                },
            ),
            "equifax": (
                uuid.uuid4(),
                {
                    "accounts": [
                        {
                            "creditor_name": "Capital One",
                            "account_number_masked": "****4242",
                            "balance": 4213.0,
                            "past_due_amount": 0.0,
                            "payment_status": "Charge Off",
                            "date_first_delinquency": "03/01/2021",
                        }
                    ]
                },
            ),
        },
    )

    capital = next(item for item in result.discrepancies if "Capital One" in item.creditor_name)
    assert "past_due_mismatch" in capital.discrepancy_types
    assert "dofd_mismatch" in capital.discrepancy_types
    assert capital.dispute_ready is True
    assert result.summary["past_due_mismatch"] == 1
    assert result.summary["dofd_mismatch"] == 1
    assert any("past_due_amount" in diff.field for diff in capital.field_diffs)
    assert any("date_first_delinquency" in diff.field for diff in capital.field_diffs)


def test_compare_cross_bureau_reports_marks_selective_reporting_as_investigation() -> None:
    case_id = uuid.uuid4()

    result = compare_cross_bureau_reports(
        case_id=case_id,
        reports_by_bureau={
            "experian": (uuid.uuid4(), {"accounts": []}),
            "equifax": (uuid.uuid4(), {"accounts": []}),
            "transunion": (
                uuid.uuid4(),
                {
                    "accounts": [
                        {
                            "creditor_name": "ACHIEVE PERSONAL LOANS",
                            "account_number_masked": "****1081",
                            "balance": 18764.0,
                            "payment_status": "Current",
                        }
                    ]
                },
            ),
        },
    )

    achieve = next(
        item for item in result.discrepancies if item.creditor_name == "ACHIEVE PERSONAL LOANS"
    )
    assert achieve.classification == "cross_bureau_reporting_difference"
    assert achieve.classification_label == "Cross-Bureau Reporting Difference"
    assert achieve.workflow_tier == "investigation"
    assert achieve.requires_investigation is True
    assert achieve.dispute_ready is False
    assert achieve.is_actionable is True
    assert achieve.bureaus_reporting == ("transunion",)
    assert achieve.bureaus_missing == ("equifax", "experian")
    assert achieve.confidence_score >= 75
    assert any(cause.likelihood == "most_likely" for cause in achieve.possible_causes)
    assert "before considering a dispute" in achieve.recommended_next_step
    assert result.summary["investigation_needed"] == 1
    assert result.summary["dispute_ready"] == 0


def test_compare_cross_bureau_reports_marks_consistent_tradelines() -> None:
    case_id = uuid.uuid4()
    result = compare_cross_bureau_reports(
        case_id=case_id,
        reports_by_bureau={
            "experian": (
                uuid.uuid4(),
                {
                    "accounts": [
                        {
                            "creditor_name": "BANK OF AMERICA",
                            "account_number_masked": "****9091",
                            "balance": 182.0,
                            "payment_status": "Collection",
                        }
                    ]
                },
            ),
            "equifax": (
                uuid.uuid4(),
                {
                    "accounts": [
                        {
                            "creditor_name": "Bank of America",
                            "account_number_masked": "****9091",
                            "balance": 182.0,
                            "payment_status": "Collection account",
                        }
                    ]
                },
            ),
        },
    )

    bank = next(item for item in result.discrepancies if "bankofamerica" in item.match_key)
    assert bank.discrepancy_types == ("consistent",)
    assert bank.workflow_tier == "none"
    assert bank.is_actionable is False
    assert bank.dispute_ready is False
