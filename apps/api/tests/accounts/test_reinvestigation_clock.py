"""Tests for the FCRA §611 reinvestigation clock (Phase 10 slice 3)."""

import uuid
from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus
from api.modules.accounts.reinvestigation import (
    compute_reinvestigation_clock,
    document_extends_window,
)
from api.modules.documents.models import Document
from tests.accounts.conftest import sample_account_payload

_TODAY = date(2026, 7, 15)


def test_compute_clock_not_sent() -> None:
    clock = compute_reinvestigation_clock(
        last_dispute_date=None, today=_TODAY, response_recorded=False
    )
    assert clock.state == "not_sent"
    assert clock.deadline is None
    assert clock.days_remaining is None


def test_compute_clock_awaiting() -> None:
    clock = compute_reinvestigation_clock(
        last_dispute_date=_TODAY, today=_TODAY, response_recorded=False
    )
    assert clock.state == "awaiting"
    assert clock.deadline == _TODAY + timedelta(days=30)
    assert clock.days_remaining == 30


def test_compute_clock_due_soon() -> None:
    clock = compute_reinvestigation_clock(
        last_dispute_date=_TODAY - timedelta(days=25), today=_TODAY, response_recorded=False
    )
    assert clock.state == "due_soon"
    assert clock.days_remaining == 5


def test_compute_clock_overdue() -> None:
    clock = compute_reinvestigation_clock(
        last_dispute_date=_TODAY - timedelta(days=40), today=_TODAY, response_recorded=False
    )
    assert clock.state == "overdue"
    assert clock.days_remaining == -10


def test_compute_clock_responded_short_circuits() -> None:
    clock = compute_reinvestigation_clock(
        last_dispute_date=_TODAY - timedelta(days=40), today=_TODAY, response_recorded=True
    )
    assert clock.state == "responded"


def test_compute_clock_extended_window_uses_45_days() -> None:
    # Day 35 is overdue on the base 30-day window but still awaiting on the 45-day window.
    start = _TODAY - timedelta(days=35)
    base = compute_reinvestigation_clock(
        last_dispute_date=start, today=_TODAY, response_recorded=False
    )
    assert base.state == "overdue"

    extended = compute_reinvestigation_clock(
        last_dispute_date=start, today=_TODAY, response_recorded=False, extended=True
    )
    assert extended.state == "awaiting"
    assert extended.extended is True
    assert extended.deadline == start + timedelta(days=45)
    assert extended.days_remaining == 10


def test_document_extends_window_within_initial_period() -> None:
    start = _TODAY
    # Supplied on day 10 of the initial 30-day window → extends.
    assert (
        document_extends_window(
            clock_start_date=start,
            document_dates=[start + timedelta(days=10)],
        )
        is True
    )


def test_document_extends_window_ignores_out_of_window_docs() -> None:
    start = _TODAY
    assert (
        document_extends_window(
            clock_start_date=start,
            document_dates=[
                start - timedelta(days=5),  # before the dispute was mailed
                start,  # same day as mailing (part of the initial packet)
                start + timedelta(days=40),  # after the initial 30-day window
            ],
        )
        is False
    )


def test_document_extends_window_no_clock_start() -> None:
    assert document_extends_window(clock_start_date=None, document_dates=[_TODAY]) is False


def _create_account_with_dispute_date(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_id: str,
    *,
    creditor_name: str,
    last_dispute_date: str | None,
) -> str:
    payload = sample_account_payload(case_id)
    payload["creditor_name"] = creditor_name
    if last_dispute_date is not None:
        payload["last_dispute_date"] = last_dispute_date
    create = api_client.post("/api/v1/accounts", headers=manager_headers, json=payload)
    assert create.status_code == 201, create.text
    return create.json()["id"]


def test_case_reinvestigation_clock_classifies_and_summarizes(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    overdue_date = (date.today() - timedelta(days=40)).isoformat()
    overdue_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Overdue Bank",
        last_dispute_date=overdue_date,
    )
    _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Awaiting Bank",
        last_dispute_date=date.today().isoformat(),
    )
    _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Not Sent Bank",
        last_dispute_date=None,
    )

    clock = api_client.get(
        "/api/v1/accounts/reinvestigation-clock",
        headers=manager_headers,
        params={"case_id": sample_case_id},
    )
    assert clock.status_code == 200
    body = clock.json()
    assert body["summary"]["overdue"] >= 1
    assert body["summary"]["awaiting"] >= 1
    assert body["summary"]["not_sent"] >= 1
    # Overdue entries are sorted first.
    assert body["accounts"][0]["state"] == "overdue"
    assert body["accounts"][0]["account_id"] == overdue_id


def test_case_reinvestigation_clock_marks_responded(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    overdue_date = (date.today() - timedelta(days=40)).isoformat()
    account_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Responded Bank",
        last_dispute_date=overdue_date,
    )

    record = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={"outcome": "verified", "response_method": "mail"},
    )
    assert record.status_code == 201

    clock = api_client.get(
        "/api/v1/accounts/reinvestigation-clock",
        headers=manager_headers,
        params={"case_id": sample_case_id},
    )
    entry = next(a for a in clock.json()["accounts"] if a["account_id"] == account_id)
    assert entry["state"] == "responded"
    assert entry["response_received"] is True
    assert entry["response_count"] == 1


async def test_clock_keys_off_latest_sent_letter(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    """A freshly sent dispute round resets the clock, overriding a stale last_dispute_date."""
    overdue_date = (date.today() - timedelta(days=40)).isoformat()
    account_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Multi Round Bank",
        last_dispute_date=overdue_date,
    )
    account = api_client.get(f"/api/v1/accounts/{account_id}", headers=manager_headers).json()

    now = datetime.now(UTC)
    db_session.add(
        DisputeLetter(
            id=uuid.uuid4(),
            organization_id=uuid.UUID(account["organization_id"]),
            case_id=uuid.UUID(sample_case_id),
            account_id=uuid.UUID(account_id),
            recipient_type="credit_bureau",
            status=DisputeLetterStatus.SENT,
            template_id="fcra_611",
            subject="Dispute",
            body="Body",
            disputed_items=["late payment"],
            requested_action="Delete the inaccurate tradeline.",
            evidence_checklist=[],
            compliance_notes=[],
            generated_by="system",
            generated_at=now,
            sent_at=now,
        )
    )
    await db_session.commit()

    clock = api_client.get(
        "/api/v1/accounts/reinvestigation-clock",
        headers=manager_headers,
        params={"case_id": sample_case_id},
    )
    entry = next(a for a in clock.json()["accounts"] if a["account_id"] == account_id)
    # Clock keys off the freshly-sent letter, not the stale account last_dispute_date.
    assert entry["clock_start_date"] == date.today().isoformat()
    assert entry["dispute_round_count"] == 1
    assert entry["state"] == "awaiting"
    assert entry["last_dispute_date"] == overdue_date


def _add_sent_letter(
    db_session: AsyncSession,
    *,
    organization_id: str,
    case_id: str,
    account_id: str,
    recipient_type: str,
    sent_at: datetime,
) -> uuid.UUID:
    letter_id = uuid.uuid4()
    db_session.add(
        DisputeLetter(
            id=letter_id,
            organization_id=uuid.UUID(organization_id),
            case_id=uuid.UUID(case_id),
            account_id=uuid.UUID(account_id),
            recipient_type=recipient_type,
            status=DisputeLetterStatus.SENT,
            template_id="fcra_611",
            subject=f"Dispute to {recipient_type}",
            body="Body",
            disputed_items=["late payment"],
            requested_action="Delete the inaccurate tradeline.",
            evidence_checklist=[],
            compliance_notes=[],
            generated_by="system",
            generated_at=sent_at,
            sent_at=sent_at,
        )
    )
    return letter_id


async def test_clock_splits_by_recipient(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    """A tradeline disputed with both a bureau and a furnisher carries two clocks."""
    account_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Two Recipient Bank",
        last_dispute_date=(date.today() - timedelta(days=40)).isoformat(),
    )
    account = api_client.get(f"/api/v1/accounts/{account_id}", headers=manager_headers).json()

    now = datetime.now(UTC)
    # Bureau round mailed 40 days ago (overdue); furnisher round mailed 5 days ago (awaiting).
    _add_sent_letter(
        db_session,
        organization_id=account["organization_id"],
        case_id=sample_case_id,
        account_id=account_id,
        recipient_type="credit_bureau",
        sent_at=now - timedelta(days=40),
    )
    _add_sent_letter(
        db_session,
        organization_id=account["organization_id"],
        case_id=sample_case_id,
        account_id=account_id,
        recipient_type="furnisher",
        sent_at=now - timedelta(days=5),
    )
    await db_session.commit()

    clock = api_client.get(
        "/api/v1/accounts/reinvestigation-clock",
        headers=manager_headers,
        params={"case_id": sample_case_id},
    )
    assert clock.status_code == 200, clock.text
    entry = next(a for a in clock.json()["accounts"] if a["account_id"] == account_id)
    recipients = {r["recipient_type"]: r for r in entry["recipients"]}
    assert set(recipients) == {"credit_bureau", "furnisher"}
    # Bureau first in the stable ordering.
    assert entry["recipients"][0]["recipient_type"] == "credit_bureau"
    assert recipients["credit_bureau"]["state"] == "overdue"
    assert recipients["credit_bureau"]["dispute_round_count"] == 1
    assert recipients["furnisher"]["state"] == "awaiting"
    assert recipients["furnisher"]["dispute_round_count"] == 1
    assert (
        recipients["furnisher"]["clock_start_date"]
        == (date.today() - timedelta(days=5)).isoformat()
    )


async def test_clock_recipient_response_resolves_only_that_recipient(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    """A response linked to the bureau letter resolves the bureau clock only."""
    account_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Selective Response Bank",
        last_dispute_date=(date.today() - timedelta(days=40)).isoformat(),
    )
    account = api_client.get(f"/api/v1/accounts/{account_id}", headers=manager_headers).json()

    now = datetime.now(UTC)
    bureau_letter_id = _add_sent_letter(
        db_session,
        organization_id=account["organization_id"],
        case_id=sample_case_id,
        account_id=account_id,
        recipient_type="credit_bureau",
        sent_at=now - timedelta(days=40),
    )
    _add_sent_letter(
        db_session,
        organization_id=account["organization_id"],
        case_id=sample_case_id,
        account_id=account_id,
        recipient_type="furnisher",
        sent_at=now - timedelta(days=40),
    )
    await db_session.commit()

    record = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={
            "outcome": "verified",
            "response_method": "mail",
            "dispute_letter_id": str(bureau_letter_id),
        },
    )
    assert record.status_code == 201, record.text

    clock = api_client.get(
        "/api/v1/accounts/reinvestigation-clock",
        headers=manager_headers,
        params={"case_id": sample_case_id},
    )
    entry = next(a for a in clock.json()["accounts"] if a["account_id"] == account_id)
    recipients = {r["recipient_type"]: r for r in entry["recipients"]}
    assert recipients["credit_bureau"]["state"] == "responded"
    assert recipients["credit_bureau"]["response_count"] == 1
    # The furnisher clock is untouched by the bureau-linked response.
    assert recipients["furnisher"]["state"] == "overdue"
    assert recipients["furnisher"]["response_count"] == 0


async def test_clock_extends_to_45_days_when_document_supplied_in_window(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    """A consumer document uploaded during the initial window extends the clock to 45 days."""
    start_date = date.today() - timedelta(days=20)
    account_id = _create_account_with_dispute_date(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Extension Bank",
        last_dispute_date=start_date.isoformat(),
    )
    account = api_client.get(f"/api/v1/accounts/{account_id}", headers=manager_headers).json()

    # Uploaded 5 days into the reinvestigation → §611(a)(1)(B) 45-day extension.
    supplied_at = datetime.now(UTC) - timedelta(days=15)
    db_session.add(
        Document(
            id=uuid.uuid4(),
            organization_id=uuid.UUID(account["organization_id"]),
            case_id=uuid.UUID(sample_case_id),
            account_id=uuid.UUID(account_id),
            title="Supplemental proof",
            file_name="proof.pdf",
            storage_key=f"docs/{uuid.uuid4()}.pdf",
            file_hash=uuid.uuid4().hex,
            created_at=supplied_at,
        )
    )
    await db_session.commit()

    clock = api_client.get(
        "/api/v1/accounts/reinvestigation-clock",
        headers=manager_headers,
        params={"case_id": sample_case_id},
    )
    body = clock.json()
    entry = next(a for a in body["accounts"] if a["account_id"] == account_id)
    assert entry["extended"] is True
    assert entry["deadline"] == (start_date + timedelta(days=45)).isoformat()
    assert entry["days_remaining"] == 25
    assert entry["state"] == "awaiting"
    assert body["summary"]["extended_windows"] >= 1
