"""Portal advisory dispute strategy suggestions (LRP-403)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import get_feature_flags
from api.modules.auth.models import Organization, User
from api.modules.cases.models import Case, CaseStatus
from api.modules.documents.strategy_run_repository import StrategyRunRepository
from tests.helpers.client_payload import sample_client_payload


@pytest.fixture(autouse=True)
def _enable_client_portal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_CLIENT_PORTAL", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


def _portal_headers_for_case(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_id: str,
    *,
    email: str,
) -> dict[str, str]:
    client_resp = api_client.post(
        "/api/v1/clients",
        headers=manager_headers,
        json=sample_client_payload(display_name="Strategy Borrower", email=email),
    )
    assert client_resp.status_code == 201, client_resp.text
    client_id = client_resp.json()["id"]
    link = api_client.patch(
        f"/api/v1/cases/{case_id}",
        headers=manager_headers,
        json={"client_id": client_id, "client_email": email},
    )
    assert link.status_code == 200, link.text
    provision = api_client.post(
        f"/api/v1/clients/{client_id}/portal-user",
        headers=manager_headers,
        json={"email": email, "password": "password123"},
    )
    assert provision.status_code == 201, provision.text
    login = api_client.post(
        "/api/v1/portal/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.mark.asyncio
async def test_portal_dispute_strategy_suggestions_from_staff_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    db_session: AsyncSession,
    test_org: Organization,
    case_manager_user: User,
) -> None:
    case = Case(
        id=uuid.uuid4(),
        organization_id=test_org.id,
        title=f"Strategy Portal {uuid.uuid4().hex[:6]}",
        client_name="Strategy Borrower",
        status=CaseStatus.OPEN,
        opened_at=datetime.now(UTC),
    )
    db_session.add(case)
    await db_session.commit()

    repo = StrategyRunRepository(db_session)
    await repo.create(
        organization_id=test_org.id,
        case_id=case.id,
        generated_by_id=case_manager_user.id,
        accounts_planned=1,
        issues_covered=2,
        payload={
            "case_id": str(case.id),
            "disclaimer": "Investigator planning aid only.",
            "summary": {
                "accounts_planned": 1,
                "issues_covered": 2,
                "high_strength_accounts": 1,
                "cfpb_recommended": 0,
                "attorney_recommended": 1,
            },
            "strategies": [
                {
                    "account_key": "acct:capital|****4242|experian",
                    "creditor_name": "Capital One",
                    "account_number_masked": "****4242",
                    "bureau": "experian",
                    "summary": "Prioritize a bureau dispute on the DOFD mismatch.",
                    "stages": [
                        {
                            "stage_order": 0,
                            "stage_kind": "cra_dispute",
                            "title": "Bureau dispute",
                            "objective": "Challenge the reporting inconsistency.",
                            "rationale": "High-strength DOFD mismatch",
                            "issue_source_ids": ["cross_bureau:x"],
                            "evidence_hints": ["Attach both bureau excerpts"],
                            "recommended": True,
                        },
                        {
                            "stage_order": 1,
                            "stage_kind": "cfpb_escalation",
                            "title": "CFPB escalation",
                            "objective": "Escalate if bureau does not correct.",
                            "rationale": "Optional",
                            "issue_source_ids": [],
                            "evidence_hints": [],
                            "recommended": False,
                        },
                    ],
                }
            ],
        },
    )
    await db_session.commit()

    portal_headers = _portal_headers_for_case(
        api_client,
        manager_headers,
        str(case.id),
        email=f"strategy-{uuid.uuid4().hex[:8]}@example.com",
    )

    response = api_client.get(
        f"/api/v1/portal/cases/{case.id}/dispute-strategy-suggestions",
        headers=portal_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["case_id"] == str(case.id)
    assert body["staff_mediated"] is True
    assert body["auto_send"] is False
    assert body["source"] == "staff_run"
    assert (
        "never files" in body["disclaimer"].lower() or "automatically" in body["disclaimer"].lower()
    )
    assert body["summary"]["accounts_planned"] == 1
    assert len(body["suggestions"]) == 1
    suggestion = body["suggestions"][0]
    assert suggestion["creditor_label"] == "Capital One"
    assert suggestion["account_number_masked"] == "****4242"
    assert "Bureau dispute" in suggestion["recommended_stage_titles"]
    assert "issue_source_ids" not in suggestion
    assert "evidence_hints" not in suggestion
    assert all("rationale" not in stage for stage in suggestion["stages"])


def test_portal_dispute_strategy_suggestions_empty_without_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_resp = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={
            "title": f"Empty Strategy {uuid.uuid4().hex[:6]}",
            "client_name": "Empty Borrower",
        },
    )
    assert case_resp.status_code == 201, case_resp.text
    case_id = case_resp.json()["id"]
    portal_headers = _portal_headers_for_case(
        api_client,
        manager_headers,
        case_id,
        email=f"empty-strategy-{uuid.uuid4().hex[:8]}@example.com",
    )
    response = api_client.get(
        f"/api/v1/portal/cases/{case_id}/dispute-strategy-suggestions",
        headers=portal_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["source"] == "none"
    assert body["auto_send"] is False
    assert body["suggestions"] == []


def test_portal_dispute_strategy_suggestions_isolation(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    case_a = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": f"A {uuid.uuid4().hex[:6]}", "client_name": "A"},
    ).json()["id"]
    case_b = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": f"B {uuid.uuid4().hex[:6]}", "client_name": "B"},
    ).json()["id"]
    portal_headers = _portal_headers_for_case(
        api_client,
        manager_headers,
        case_a,
        email=f"iso-strategy-{uuid.uuid4().hex[:8]}@example.com",
    )
    forbidden = api_client.get(
        f"/api/v1/portal/cases/{case_b}/dispute-strategy-suggestions",
        headers=portal_headers,
    )
    assert forbidden.status_code in {403, 404}
