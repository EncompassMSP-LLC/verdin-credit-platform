"""Tests for the litigation-readiness evidence packet (Phase 11 slice 5)."""

import uuid
from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.accounts.dispute_letter_models import DisputeLetter, DisputeLetterStatus
from api.modules.accounts.litigation_packet import (
    LitigationReadinessInputs,
    build_litigation_readiness,
)
from tests.accounts.conftest import sample_account_payload


def _inputs(**overrides: object) -> LitigationReadinessInputs:
    base: dict[str, object] = {
        "clock_state": "awaiting",
        "latest_outcome": None,
        "dispute_round": 1,
        "risk_score": None,
        "sent_letter_count": 0,
        "response_count": 0,
    }
    base.update(overrides)
    return LitigationReadinessInputs(**base)  # type: ignore[arg-type]


def test_readiness_resolved_outcome_not_ready() -> None:
    readiness = build_litigation_readiness(_inputs(latest_outcome="deleted"))
    assert readiness.eligible is False
    assert readiness.strength == "not_ready"
    assert readiness.score == 0
    assert readiness.indicators == []


def test_readiness_no_signals_not_ready() -> None:
    readiness = build_litigation_readiness(_inputs())
    assert readiness.eligible is False
    assert readiness.strength == "not_ready"
    assert readiness.score == 0
    assert "No willful-noncompliance indicators" in readiness.summary


def test_readiness_overdue_only_is_moderate() -> None:
    readiness = build_litigation_readiness(_inputs(clock_state="overdue"))
    assert readiness.score == 30
    assert readiness.strength == "moderate"
    assert readiness.eligible is True
    assert any("missed the §611" in indicator for indicator in readiness.indicators)


def test_readiness_verified_high_strength_multi_round_is_strong() -> None:
    readiness = build_litigation_readiness(
        _inputs(
            clock_state="responded",
            latest_outcome="verified",
            dispute_round=2,
            risk_score=90,
            sent_letter_count=2,
            response_count=2,
        )
    )
    # verified (20) + high-strength (30) + multi-round (25) = 75.
    assert readiness.score == 75
    assert readiness.strength == "strong"
    assert readiness.eligible is True


def test_readiness_score_caps_at_100() -> None:
    readiness = build_litigation_readiness(
        _inputs(
            clock_state="overdue",
            latest_outcome="verified",
            dispute_round=3,
            risk_score=95,
            sent_letter_count=3,
            response_count=3,
        )
    )
    assert readiness.score == 100
    assert readiness.strength == "strong"


def test_readiness_rejected_is_weak() -> None:
    readiness = build_litigation_readiness(_inputs(latest_outcome="rejected"))
    assert readiness.score == 25
    assert readiness.strength == "weak"
    assert readiness.eligible is False


def _create_account(
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


def _add_sent_letter(
    db_session: AsyncSession,
    *,
    organization_id: str,
    case_id: str,
    account_id: str,
    subject: str,
) -> None:
    now = datetime.now(UTC)
    db_session.add(
        DisputeLetter(
            id=uuid.uuid4(),
            organization_id=uuid.UUID(organization_id),
            case_id=uuid.UUID(case_id),
            account_id=uuid.UUID(account_id),
            recipient_type="credit_bureau",
            status=DisputeLetterStatus.SENT,
            template_id="fcra_611",
            subject=subject,
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


async def test_litigation_packet_grades_multi_round_verified_trail(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    account_id = _create_account(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Litigation Bank",
        last_dispute_date=date.today().isoformat(),
    )
    account = api_client.get(f"/api/v1/accounts/{account_id}", headers=manager_headers).json()

    # Two mailed rounds → pattern of inadequate reinvestigation.
    for subject in ("Dispute round 1", "Dispute round 2"):
        _add_sent_letter(
            db_session,
            organization_id=account["organization_id"],
            case_id=sample_case_id,
            account_id=account_id,
            subject=subject,
        )
    await db_session.commit()

    record = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={"outcome": "verified", "response_method": "mail"},
    )
    assert record.status_code == 201

    packet = api_client.get(
        f"/api/v1/accounts/{account_id}/litigation-packet",
        headers=manager_headers,
    )
    assert packet.status_code == 200, packet.text
    body = packet.json()
    assert body["account_id"] == account_id
    assert body["latest_outcome"] == "verified"
    # verified (20) + multi-round (25) → moderate, eligible for attorney handoff.
    assert body["assessment"]["strength"] in {"moderate", "strong"}
    assert body["assessment"]["eligible"] is True
    assert body["dispute_round"] >= 2
    assert len(body["responses"]) == 1
    assert len(body["letters"]) == 2
    assert "attorney" in body["disclaimer"].lower()


def test_litigation_packet_single_verified_response_is_weak(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    account_id = _create_account(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Single Round Bank",
        last_dispute_date=(date.today() - timedelta(days=40)).isoformat(),
    )
    record = api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={"outcome": "verified", "response_method": "mail"},
    )
    assert record.status_code == 201

    packet = api_client.get(
        f"/api/v1/accounts/{account_id}/litigation-packet",
        headers=manager_headers,
    )
    assert packet.status_code == 200, packet.text
    body = packet.json()
    # A recorded response stops the §611 clock, so a lone verified round is only "weak".
    assert body["latest_outcome"] == "verified"
    assert body["clock_state"] == "responded"
    assert body["assessment"]["strength"] == "weak"
    assert body["assessment"]["eligible"] is False


async def test_litigation_packet_lists_sent_letters(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
    db_session: AsyncSession,
) -> None:
    account_id = _create_account(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Evidence Bank",
        last_dispute_date=date.today().isoformat(),
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
            subject="Dispute round 1",
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

    packet = api_client.get(
        f"/api/v1/accounts/{account_id}/litigation-packet",
        headers=manager_headers,
    )
    assert packet.status_code == 200, packet.text
    body = packet.json()
    assert len(body["letters"]) == 1
    assert body["letters"][0]["subject"] == "Dispute round 1"
    assert body["letters"][0]["status"] == "sent"
    assert body["dispute_round"] >= 1


def test_litigation_packet_requires_write_permission(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    account_id = _create_account(
        api_client,
        manager_headers,
        sample_case_id,
        creditor_name="Locked Bank",
        last_dispute_date=date.today().isoformat(),
    )
    forbidden = api_client.get(
        f"/api/v1/accounts/{account_id}/litigation-packet",
        headers=readonly_headers,
    )
    assert forbidden.status_code == 403
