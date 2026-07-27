"""LRP-109 — production organization mode guardrails."""

import pytest
from fastapi.testclient import TestClient

from api.core.config import get_settings
from api.modules.auth.models import Organization, OrganizationType
from api.modules.org_context.models import OrgDemoFeature


def test_production_org_context_has_no_demo_capabilities(
    api_client: TestClient,
    production_admin_headers: dict[str, str],
    production_org: Organization,
) -> None:
    response = api_client.get("/api/v1/org-context", headers=production_admin_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["organization_id"] == str(production_org.id)
    assert body["organization_type"] == OrganizationType.PRODUCTION.value
    assert body["demo_capabilities_allowed"] is False
    assert body["feature_flags"]["sample_borrowers"] is False


def test_demo_org_context_allows_demo_capabilities(
    api_client: TestClient,
    demo_admin_headers: dict[str, str],
    demo_org: Organization,
) -> None:
    response = api_client.get("/api/v1/org-context", headers=demo_admin_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["organization_id"] == str(demo_org.id)
    assert body["organization_type"] == OrganizationType.DEMO.value
    assert body["demo_capabilities_allowed"] is True
    assert body["feature_flags"]["sample_borrowers"] is True


def test_sample_borrowers_blocked_for_production(
    api_client: TestClient,
    production_admin_headers: dict[str, str],
) -> None:
    response = api_client.post(
        "/api/v1/org-context/demo/sample-borrowers",
        headers=production_admin_headers,
        json={"count": 2},
    )
    assert response.status_code == 403, response.text
    assert "production" in response.json()["detail"].lower()


def test_sample_borrowers_allowed_for_demo(
    api_client: TestClient,
    demo_admin_headers: dict[str, str],
    demo_org: Organization,
) -> None:
    response = api_client.post(
        "/api/v1/org-context/demo/sample-borrowers",
        headers=demo_admin_headers,
        json={"count": 2},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["organization_id"] == str(demo_org.id)
    assert len(body["created_client_ids"]) == 2
    assert body["feature"] == OrgDemoFeature.SAMPLE_BORROWERS.value


def test_cannot_enable_demo_flag_on_production(
    api_client: TestClient,
    production_admin_headers: dict[str, str],
) -> None:
    response = api_client.put(
        "/api/v1/org-context/feature-flags",
        headers=production_admin_headers,
        json={"feature": "sample_borrowers", "enabled": True},
    )
    assert response.status_code == 403, response.text


def test_fake_credit_report_blocked_for_production(
    api_client: TestClient,
    production_admin_headers: dict[str, str],
) -> None:
    response = api_client.post(
        "/api/v1/org-context/demo/fake-credit-report",
        headers=production_admin_headers,
    )
    assert response.status_code == 403, response.text


def test_fake_credit_report_deferred_for_demo(
    api_client: TestClient,
    demo_admin_headers: dict[str, str],
) -> None:
    response = api_client.post(
        "/api/v1/org-context/demo/fake-credit-report",
        headers=demo_admin_headers,
    )
    assert response.status_code == 501, response.text


def test_sample_data_env_blocks_demo_generation(
    api_client: TestClient,
    demo_admin_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_SAMPLE_DATA", "false")
    get_settings.cache_clear()
    try:
        response = api_client.post(
            "/api/v1/org-context/demo/sample-borrowers",
            headers=demo_admin_headers,
            json={"count": 1},
        )
        assert response.status_code == 403, response.text
    finally:
        get_settings.cache_clear()


def test_migration_default_organization_type_is_production(
    production_org: Organization,
) -> None:
    assert production_org.organization_type == OrganizationType.PRODUCTION
