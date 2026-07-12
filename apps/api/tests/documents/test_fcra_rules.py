"""Unit tests for FCRA statutory checklist rule evaluation."""

from __future__ import annotations

import uuid

from api.modules.documents.fcra_rules import evaluate_tradelines


def test_evaluate_tradelines_flags_obsolete_and_adverse_missing_dofd() -> None:
    document_id = uuid.uuid4()
    result = evaluate_tradelines(
        document_id=document_id,
        bureau="experian",
        parsed_report={
            "schema_version": "1.1",
            "accounts": [
                {
                    "creditor_name": "Old Lender",
                    "account_number_masked": "****4242",
                    "account_status": "Charge Off",
                    "balance": 1200.0,
                    "past_due_amount": 1200.0,
                    "date_first_delinquency": "01/15/2015",
                    "date_reported": "06/01/2024",
                },
                {
                    "creditor_name": "No Dofd Bank",
                    "account_number_masked": "****1111",
                    "account_status": "Collection",
                    "past_due_amount": 400.0,
                    "date_reported": "06/01/2024",
                },
            ],
        },
    )

    rule_ids = {finding.rule_id for finding in result.findings}
    assert "fcra.obsolete_adverse_info" in rule_ids
    assert "fcra.adverse_missing_dofd" in rule_ids
    assert result.as_of_date == "2024-06-01"
    assert result.summary["tradelines_evaluated"] == 2
    assert result.document_id == document_id
    obsolete = next(f for f in result.findings if f.rule_id == "fcra.obsolete_adverse_info")
    assert "605" in obsolete.fcra_sections


def test_evaluate_tradelines_flags_collection_original_creditor_and_past_due() -> None:
    result = evaluate_tradelines(
        document_id=uuid.uuid4(),
        bureau="equifax",
        parsed_report={
            "accounts": [
                {
                    "creditor_name": "ABC Collections",
                    "account_number_masked": "****9999",
                    "account_status": "Collection",
                    "balance": 500.0,
                    "past_due_amount": 800.0,
                    "date_reported": "03/01/2024",
                }
            ]
        },
    )
    rule_ids = {finding.rule_id for finding in result.findings}
    assert "fcra.collection_missing_original_creditor" in rule_ids
    assert "fcra.past_due_exceeds_balance" in rule_ids
    assert "fcra.adverse_missing_dofd" in rule_ids


def test_evaluate_tradelines_flags_impossible_as_of_timeline() -> None:
    result = evaluate_tradelines(
        document_id=uuid.uuid4(),
        bureau="transunion",
        parsed_report={
            "accounts": [
                {
                    "creditor_name": "Future Bank",
                    "account_number_masked": "****2222",
                    "open_date": "12/01/2025",
                    "date_first_delinquency": "01/15/2026",
                    "account_status": "Open",
                    "payment_status": "Current",
                    "date_reported": "06/01/2024",
                }
            ]
        },
    )
    rule_ids = {finding.rule_id for finding in result.findings}
    assert "fcra.open_date_after_as_of" in rule_ids
    assert "fcra.dofd_after_as_of" in rule_ids


def test_evaluate_tradelines_flags_closed_and_sold_balance() -> None:
    result = evaluate_tradelines(
        document_id=uuid.uuid4(),
        bureau="experian",
        parsed_report={
            "accounts": [
                {
                    "creditor_name": "Closed Bank",
                    "account_number_masked": "****1001",
                    "account_status": "Closed",
                    "payment_status": "Paid",
                    "date_reported": "06/01/2024",
                },
                {
                    "creditor_name": "Sold Card",
                    "account_number_masked": "****1002",
                    "account_status": "Open",
                    "remarks": "Account sold to another lender",
                    "balance": 2500.0,
                    "date_reported": "06/01/2024",
                },
            ]
        },
    )
    rule_ids = {finding.rule_id for finding in result.findings}
    assert "fcra.closed_missing_date_closed" in rule_ids
    assert "fcra.sold_transferred_still_balance" in rule_ids
