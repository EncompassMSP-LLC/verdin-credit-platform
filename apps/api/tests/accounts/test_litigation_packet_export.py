"""Tests for the operator-gated litigation-packet text export (Phase 12 slice 5)."""

import uuid
from datetime import UTC, date, datetime

from fastapi.testclient import TestClient

from api.modules.accounts.litigation_packet_export import (
    build_litigation_packet_text,
    export_filename,
    sanitize_content_disposition_filename,
)
from api.modules.accounts.schemas import (
    AccountLitigationPacket,
    LitigationCrossBureauDiscrepancy,
    LitigationCrossBureauEvidence,
    LitigationPacketLetter,
    LitigationPacketResponse,
    LitigationReadinessAssessment,
)
from tests.accounts.conftest import sample_account_payload


def _packet(**overrides: object) -> AccountLitigationPacket:
    base = AccountLitigationPacket(
        account_id=uuid.uuid4(),
        case_id=uuid.uuid4(),
        creditor_name="Export Bank",
        bureau="experian",
        dispute_status="verified",
        dispute_round=2,
        risk_score=85,
        generated_at=datetime.now(UTC),
        clock_state="responded",
        clock_deadline=date.today(),
        clock_extended=True,
        latest_outcome="verified",
        recommended_action="escalate_attorney",
        assessment=LitigationReadinessAssessment(
            eligible=True,
            strength="strong",
            score=75,
            indicators=["Bureau verified the disputed tradeline as accurate."],
            summary="Willful-noncompliance indicators are present.",
        ),
        cross_bureau=LitigationCrossBureauEvidence(
            compared_bureaus=["equifax"],
            discrepancies=[
                LitigationCrossBureauDiscrepancy(
                    kind="outcome_conflict",
                    bureau="equifax",
                    detail="Verified here but deleted at equifax.",
                )
            ],
        ),
        letters=[
            LitigationPacketLetter(
                id=uuid.uuid4(),
                recipient_type="credit_bureau",
                status="sent",
                subject="Dispute round 1",
                disputed_items=["late payment"],
                generated_at=datetime.now(UTC),
                sent_at=datetime.now(UTC),
            )
        ],
        responses=[
            LitigationPacketResponse(
                id=uuid.uuid4(),
                outcome="verified",
                response_method="mail",
                response_date=date.today(),
                recorded_at=datetime.now(UTC),
                notes=None,
            )
        ],
        disclaimer="Advisory evidence bundle for attorney review only.",
    )
    return base.model_copy(update=overrides)


def test_export_text_includes_disclaimer_and_evidence() -> None:
    text = build_litigation_packet_text(_packet())
    assert "LITIGATION-READINESS EVIDENCE PACKET" in text
    assert "Advisory evidence bundle for attorney review only." in text
    assert "Export Bank" in text
    assert "CROSS-BUREAU DISCREPANCIES" in text
    assert "outcome_conflict" in text
    assert "Dispute round 1" in text
    assert "verified via mail" in text
    assert text.endswith("\n")


def test_export_text_handles_empty_cross_bureau() -> None:
    packet = _packet(
        cross_bureau=LitigationCrossBureauEvidence(compared_bureaus=[], discrepancies=[])
    )
    text = build_litigation_packet_text(packet)
    assert "no same-creditor tradelines at other bureaus" in text


def test_export_filename_and_sanitize() -> None:
    packet = _packet()
    name = export_filename(packet, "text")
    assert name.startswith("litigation-packet-")
    assert name.endswith(".txt")
    assert sanitize_content_disposition_filename("a b/c.txt") == "a_b_c.txt"


def _create_account(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_id: str,
    *,
    creditor_name: str,
) -> str:
    payload = sample_account_payload(case_id)
    payload["creditor_name"] = creditor_name
    payload["last_dispute_date"] = date.today().isoformat()
    create = api_client.post("/api/v1/accounts", headers=manager_headers, json=payload)
    assert create.status_code == 201, create.text
    return create.json()["id"]


def test_export_endpoint_returns_text_attachment(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    account_id = _create_account(
        api_client, manager_headers, sample_case_id, creditor_name="Endpoint Bank"
    )
    api_client.post(
        f"/api/v1/accounts/{account_id}/dispute-responses",
        headers=manager_headers,
        json={"outcome": "verified", "response_method": "mail"},
    )
    response = api_client.get(
        f"/api/v1/accounts/{account_id}/litigation-packet/export",
        headers=manager_headers,
        params={"format": "text"},
    )
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("text/plain")
    assert "attachment; filename=" in response.headers["content-disposition"]
    assert "LITIGATION-READINESS EVIDENCE PACKET" in response.text
    assert "Endpoint Bank" in response.text


def test_export_endpoint_requires_write_permission(
    api_client: TestClient,
    manager_headers: dict[str, str],
    readonly_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    account_id = _create_account(
        api_client, manager_headers, sample_case_id, creditor_name="Locked Export Bank"
    )
    forbidden = api_client.get(
        f"/api/v1/accounts/{account_id}/litigation-packet/export",
        headers=readonly_headers,
        params={"format": "text"},
    )
    assert forbidden.status_code == 403
