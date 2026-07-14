"""Tests for persisted dispute strategy runs."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.auth.models import Organization, User
from api.modules.cases.models import Case, CaseStatus
from api.modules.documents.schemas import (
    CaseDisputeStrategyResponse,
    DisputeStrategySummary,
)
from api.modules.documents.strategy_run_repository import StrategyRunRepository


@pytest.fixture
async def sample_case(
    db_session: AsyncSession,
    test_org: Organization,
) -> Case:
    case = Case(
        id=uuid.uuid4(),
        organization_id=test_org.id,
        title="Strategy Run Case",
        client_name="Run Client",
        status=CaseStatus.OPEN,
        opened_at=datetime.now(UTC),
    )
    db_session.add(case)
    await db_session.commit()
    return case


async def test_strategy_run_repository_list_for_case(
    db_session: AsyncSession,
    test_org: Organization,
    case_manager_user: User,
    sample_case: Case,
) -> None:
    repo = StrategyRunRepository(db_session)
    payload = {
        "case_id": str(sample_case.id),
        "disclaimer": "Staff-mediated planning aid only.",
        "summary": {
            "accounts_planned": 1,
            "issues_covered": 1,
            "high_strength_accounts": 0,
            "cfpb_recommended": 0,
            "attorney_recommended": 0,
        },
        "strategies": [],
    }
    for issues_covered in (1, 2):
        await repo.create(
            organization_id=test_org.id,
            case_id=sample_case.id,
            generated_by_id=case_manager_user.id,
            accounts_planned=1,
            issues_covered=issues_covered,
            payload=payload,
        )
    await db_session.commit()

    from api.modules.documents.strategy_run_repository import StrategyRunListFilters

    runs, total = await repo.list_for_case(
        StrategyRunListFilters(
            organization_id=test_org.id,
            case_id=sample_case.id,
            skip=0,
            limit=10,
        )
    )
    assert total == 2
    assert len(runs) == 2


async def test_strategy_run_repository_create_and_get_latest(
    db_session: AsyncSession,
    test_org: Organization,
    case_manager_user: User,
    sample_case: Case,
) -> None:
    repo = StrategyRunRepository(db_session)
    payload = {
        "case_id": str(sample_case.id),
        "disclaimer": "Staff-mediated planning aid only.",
        "summary": {
            "accounts_planned": 1,
            "issues_covered": 2,
            "high_strength_accounts": 0,
            "cfpb_recommended": 0,
            "attorney_recommended": 0,
        },
        "strategies": [],
    }

    created = await repo.create(
        organization_id=test_org.id,
        case_id=sample_case.id,
        generated_by_id=case_manager_user.id,
        accounts_planned=1,
        issues_covered=2,
        payload=payload,
    )
    await db_session.commit()

    latest = await repo.get_latest_for_case(
        organization_id=test_org.id,
        case_id=sample_case.id,
    )
    assert latest is not None
    assert latest.id == created.id
    assert latest.payload["disclaimer"] == payload["disclaimer"]


def test_get_case_dispute_strategy_persists_run(
    api_client: TestClient,
    manager_headers: dict[str, str],
    sample_case_id: str,
) -> None:
    strategy_response = CaseDisputeStrategyResponse(
        case_id=uuid.UUID(sample_case_id),
        disclaimer="Staff-mediated planning aid only.",
        summary=DisputeStrategySummary(
            accounts_planned=0,
            issues_covered=0,
            high_strength_accounts=0,
            cfpb_recommended=0,
            attorney_recommended=0,
        ),
        strategies=[],
    )

    with patch(
        "api.modules.documents.service.DocumentService._build_case_dispute_strategy_response",
        new_callable=AsyncMock,
        return_value=strategy_response,
    ):
        response = api_client.get(
            f"/api/v1/cases/{sample_case_id}/dispute-strategy",
            headers=manager_headers,
        )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["run_id"] is not None
    assert data["generated_at"] is not None

    latest = api_client.get(
        f"/api/v1/cases/{sample_case_id}/dispute-strategy/runs/latest",
        headers=manager_headers,
    )
    assert latest.status_code == 200, latest.text
    latest_data = latest.json()
    assert latest_data["id"] == data["run_id"]
    assert latest_data["case_id"] == sample_case_id
    assert latest_data["accounts_planned"] == data["summary"]["accounts_planned"]
    assert latest_data["issues_covered"] == data["summary"]["issues_covered"]

    listed = api_client.get(
        f"/api/v1/cases/{sample_case_id}/dispute-strategy/runs",
        headers=manager_headers,
    )
    assert listed.status_code == 200, listed.text
    listed_data = listed.json()
    assert listed_data["total"] >= 1
    assert any(item["id"] == data["run_id"] for item in listed_data["items"])


def test_get_latest_dispute_strategy_run_not_found(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    create = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "No Strategy Run", "client_name": "Run Client"},
    )
    assert create.status_code == 201, create.text
    case_id = create.json()["id"]

    response = api_client.get(
        f"/api/v1/cases/{case_id}/dispute-strategy/runs/latest",
        headers=manager_headers,
    )
    assert response.status_code == 404
