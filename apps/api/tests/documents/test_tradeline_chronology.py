"""Unit tests for multi-snapshot tradeline chronology."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from api.modules.documents.tradeline_chronology import (
    ReportSnapshotInput,
    build_case_tradeline_chronology,
)


def _report(
    *,
    bureau: str,
    parsed_at: datetime,
    accounts: list[dict],
    document_id: uuid.UUID | None = None,
) -> ReportSnapshotInput:
    return ReportSnapshotInput(
        document_id=document_id or uuid.uuid4(),
        bureau=bureau,
        parsed_at=parsed_at,
        parsed_report={"schema_version": "1.1", "accounts": accounts},
    )


def test_chronology_flags_balance_increase_and_status_change() -> None:
    case_id = uuid.uuid4()
    jan = _report(
        bureau="experian",
        parsed_at=datetime(2024, 1, 15, tzinfo=UTC),
        accounts=[
            {
                "creditor_name": "Capital One",
                "account_number_masked": "****4242",
                "balance": 5200.0,
                "account_status": "Charge Off",
                "payment_status": "Charge Off",
                "date_reported": "01/10/2024",
            }
        ],
    )
    feb = _report(
        bureau="experian",
        parsed_at=datetime(2024, 2, 15, tzinfo=UTC),
        accounts=[
            {
                "creditor_name": "Capital One",
                "account_number_masked": "****4242",
                "balance": 4800.0,
                "account_status": "Charge Off",
                "payment_status": "Charge Off",
                "date_reported": "02/10/2024",
            }
        ],
    )
    mar = _report(
        bureau="experian",
        parsed_at=datetime(2024, 3, 15, tzinfo=UTC),
        accounts=[
            {
                "creditor_name": "Capital One",
                "account_number_masked": "****4242",
                "balance": 5200.0,
                "account_status": "Collection",
                "payment_status": "Collection",
                "date_reported": "03/10/2024",
            }
        ],
    )

    result = build_case_tradeline_chronology(
        case_id=case_id,
        reports=[mar, jan, feb],
    )

    assert result.reports_evaluated == 3
    assert result.summary["tradelines"] == 1
    assert result.summary["with_changes"] == 1
    tradeline = result.tradelines[0]
    assert tradeline.creditor_name == "Capital One"
    assert tradeline.snapshot_count == 3
    event_types = {event.event_type for event in tradeline.events}
    assert "balance_decreased" in event_types
    assert "balance_increased" in event_types
    assert "status_changed" in event_types
    increased = next(e for e in tradeline.events if e.event_type == "balance_increased")
    assert increased.previous == 4800.0
    assert increased.current == 5200.0
    assert increased.severity == "high"


def test_chronology_flags_appeared_and_disappeared() -> None:
    case_id = uuid.uuid4()
    first = _report(
        bureau="equifax",
        parsed_at=datetime(2024, 1, 1, tzinfo=UTC),
        accounts=[
            {
                "creditor_name": "Retail Card",
                "account_number_masked": "****1111",
                "balance": 100.0,
                "account_status": "Open",
            }
        ],
    )
    second = _report(
        bureau="equifax",
        parsed_at=datetime(2024, 2, 1, tzinfo=UTC),
        accounts=[
            {
                "creditor_name": "New Lender",
                "account_number_masked": "****2222",
                "balance": 50.0,
                "account_status": "Open",
            }
        ],
    )

    result = build_case_tradeline_chronology(case_id=case_id, reports=[first, second])
    by_creditor = {item.creditor_name: item for item in result.tradelines}
    assert "Retail Card" in by_creditor
    assert "New Lender" in by_creditor
    assert any(e.event_type == "disappeared" for e in by_creditor["Retail Card"].events)
    assert any(e.event_type == "appeared" for e in by_creditor["New Lender"].events)


def test_chronology_bureau_filter() -> None:
    case_id = uuid.uuid4()
    reports = [
        _report(
            bureau="experian",
            parsed_at=datetime(2024, 1, 1, tzinfo=UTC),
            accounts=[
                {
                    "creditor_name": "Bank A",
                    "account_number_masked": "****1",
                    "balance": 10.0,
                }
            ],
        ),
        _report(
            bureau="transunion",
            parsed_at=datetime(2024, 1, 2, tzinfo=UTC),
            accounts=[
                {
                    "creditor_name": "Bank B",
                    "account_number_masked": "****2",
                    "balance": 20.0,
                }
            ],
        ),
    ]
    result = build_case_tradeline_chronology(
        case_id=case_id,
        reports=reports,
        bureau="experian",
    )
    assert result.bureaus == ("experian",)
    assert result.summary["tradelines"] == 1
    assert result.tradelines[0].creditor_name == "Bank A"
