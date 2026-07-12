"""Unit tests for Metro 2 consistency rule evaluation."""

from __future__ import annotations

import uuid

from api.modules.documents.metro2_rules import evaluate_tradelines


def test_evaluate_tradelines_flags_closed_with_balance_and_past_due_without_dofd() -> None:
    document_id = uuid.uuid4()
    result = evaluate_tradelines(
        document_id=document_id,
        bureau="experian",
        parsed_report={
            "schema_version": "1.1",
            "accounts": [
                {
                    "creditor_name": "Capital One",
                    "account_number_masked": "****4242",
                    "account_status": "Closed",
                    "payment_status": "Charge Off",
                    "balance": 4213.0,
                    "past_due_amount": 4213.0,
                    "date_first_delinquency": None,
                },
                {
                    "creditor_name": "Clean Bank",
                    "account_number_masked": "****1111",
                    "account_status": "Open",
                    "payment_status": "Current",
                    "balance": 100.0,
                    "past_due_amount": 0.0,
                },
            ],
        },
    )

    rule_ids = {finding.rule_id for finding in result.findings}
    assert "metro2.closed_with_balance" in rule_ids
    assert "metro2.past_due_without_dofd" in rule_ids
    assert result.summary["high"] >= 2
    assert result.summary["tradelines_evaluated"] == 2
    assert result.document_id == document_id
    assert result.bureau == "experian"
    assert result.schema_version == "1.1"


def test_evaluate_tradelines_flags_impossible_dates_and_balance_vs_high_credit() -> None:
    result = evaluate_tradelines(
        document_id=uuid.uuid4(),
        bureau="equifax",
        parsed_report={
            "accounts": [
                {
                    "creditor_name": "Metro Auto",
                    "account_number_masked": "****9999",
                    "open_date": "01/15/2022",
                    "date_closed": "01/01/2021",
                    "balance": 9000.0,
                    "high_credit": 5000.0,
                    "account_status": "Open",
                    "payment_status": "Current",
                }
            ]
        },
    )

    rule_ids = {finding.rule_id for finding in result.findings}
    assert "metro2.date_closed_before_open" in rule_ids
    assert "metro2.balance_exceeds_high_credit" in rule_ids


def test_evaluate_tradelines_flags_current_with_past_due() -> None:
    result = evaluate_tradelines(
        document_id=uuid.uuid4(),
        bureau="transunion",
        parsed_report={
            "accounts": [
                {
                    "creditor_name": "Retail Card",
                    "account_number_masked": "****2222",
                    "payment_status": "Pays As Agreed",
                    "past_due_amount": 250.0,
                    "date_first_delinquency": "06/01/2024",
                }
            ]
        },
    )

    assert any(finding.rule_id == "metro2.current_with_past_due" for finding in result.findings)


def test_evaluate_tradelines_flags_charge_off_dofd_and_zero_balance_past_due() -> None:
    result = evaluate_tradelines(
        document_id=uuid.uuid4(),
        bureau="experian",
        parsed_report={
            "accounts": [
                {
                    "creditor_name": "Lender A",
                    "account_number_masked": "****1001",
                    "account_status": "Charge Off",
                    "balance": 1200.0,
                    "past_due_amount": 0.0,
                },
                {
                    "creditor_name": "Lender B",
                    "account_number_masked": "****1002",
                    "open_date": "02/01/2022",
                    "date_first_delinquency": "01/01/2021",
                    "payment_status": "Late 30",
                    "past_due_amount": 100.0,
                },
                {
                    "creditor_name": "Lender C",
                    "account_number_masked": "****1003",
                    "balance": 0.0,
                    "past_due_amount": 75.0,
                },
                {
                    "creditor_name": "Lender D",
                    "account_number_masked": "****1004",
                    "payment_status": "Current",
                    "account_status": "Open",
                    "date_closed": "05/01/2024",
                },
            ]
        },
    )
    rule_ids = {finding.rule_id for finding in result.findings}
    assert "metro2.charge_off_zero_past_due" in rule_ids
    assert "metro2.dofd_before_open" in rule_ids
    assert "metro2.zero_balance_with_past_due" in rule_ids
    assert "metro2.open_with_date_closed" in rule_ids
