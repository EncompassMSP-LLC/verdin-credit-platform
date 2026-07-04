"""Predictive analytics reporting tests."""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.feature_flags import get_feature_flags
from api.core.predictive_analytics import build_predictive_outcomes, compute_outcome_score
from api.modules.auth.models import Organization
from api.modules.cases.models import Case, CasePriority, CaseStage, CaseStatus


@pytest.fixture
def predictive_analytics_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_PREDICTIVE_ANALYTICS", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


def test_compute_outcome_score() -> None:
    assert (
        compute_outcome_score(
            total_cases=0,
            cases_closed_90d=0,
            disputed_accounts=0,
            accounts_dispute_resolved=0,
            dispute_letters_sent=0,
        )
        == 0
    )
    assert (
        compute_outcome_score(
            total_cases=10,
            cases_closed_90d=10,
            disputed_accounts=5,
            accounts_dispute_resolved=5,
            dispute_letters_sent=3,
        )
        == 100
    )


def test_build_predictive_outcomes_rates() -> None:
    payload = build_predictive_outcomes(
        cases_by_status={"open": 2, "closed": 8},
        accounts_by_dispute_status={"not_started": 1, "dispute_sent": 2, "corrected": 1},
        dispute_letters_by_status={"draft": 1, "sent": 2},
        cases_closed_30d=3,
        cases_closed_90d=5,
        accounts_dispute_resolved=1,
        dispute_letters_sent=2,
    )
    assert payload["total_cases"] == 10
    assert payload["disputed_accounts"] == 3
    assert payload["case_closure_rate_90d"] == 50.0
    assert payload["dispute_resolution_rate"] == pytest.approx(33.33)
    assert payload["outcome_score"] > 0


def test_predictive_outcomes_hidden_when_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = api_client.get("/api/v1/reporting/predictive/outcomes", headers=manager_headers)
    assert response.status_code == 404


@pytest.fixture
async def closed_case(db_session: AsyncSession, test_org: Organization) -> Case:
    now = datetime.now(UTC)
    case = Case(
        organization_id=test_org.id,
        title="Closed predictive case",
        client_name="Predictive Client",
        status=CaseStatus.CLOSED,
        stage=CaseStage.COMPLETE,
        priority=CasePriority.MEDIUM,
        opened_at=now - timedelta(days=45),
        closed_at=now - timedelta(days=5),
    )
    db_session.add(case)
    await db_session.commit()
    return case


def test_get_predictive_outcomes_reporting(
    api_client: TestClient,
    manager_headers: dict[str, str],
    admin_headers: dict[str, str],
    predictive_analytics_env: None,
    closed_case: Case,
) -> None:
    response = api_client.get("/api/v1/reporting/predictive/outcomes", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    outcomes = payload["predictive_outcomes"]
    assert outcomes["total_cases"] >= 1
    assert outcomes["cases_closed_90d"] >= 1
    assert "outcome_score" in outcomes

    refresh = api_client.post("/api/v1/reporting/predictive/refresh", headers=admin_headers)
    assert refresh.status_code == 200, refresh.text
    assert refresh.json()["run"]["status"] == "completed"

    refreshed = api_client.get("/api/v1/reporting/predictive/outcomes", headers=manager_headers)
    assert refreshed.status_code == 200
    assert refreshed.json()["predictive_outcomes"]["last_refreshed_at"] is not None


def test_predictive_status_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    predictive_analytics_env: None,
) -> None:
    response = api_client.get("/api/v1/reporting/predictive/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["blockers"] == []


def test_enterprise_reporting_includes_predictive_when_enabled(
    predictive_analytics_env: None,
) -> None:
    from api.core.enterprise_reporting import get_enterprise_reporting_status

    status = get_enterprise_reporting_status()
    assert "predictive_outcomes" in status.capabilities
    assert "predictive_outcomes" not in status.deferred_capabilities
