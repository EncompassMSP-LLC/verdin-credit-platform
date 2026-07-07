"""Admin-gated OAuth marketplace publishing integration tests."""

import uuid

from fastapi.testclient import TestClient


def _prepare_approved_oauth_developer_app(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> str:
    create = api_client.post(
        "/api/v1/org-admin/developer-portal/oauth-apps",
        headers=admin_headers,
        json={
            "name": "Marketplace Partner App",
            "redirect_uri": "https://example.partner.test/oauth/callback",
            "scopes": ["read"],
        },
    )
    assert create.status_code == 201, create.text
    app_id = create.json()["id"]

    approve = api_client.post(
        f"/api/v1/org-admin/developer-portal/oauth-apps/{app_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["status"] == "approved"
    return app_id


def test_oauth_marketplace_publishing_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    public_oauth_portal_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/org-admin/developer-portal/oauth-marketplace-publishing/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_oauth_marketplace_publishing_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    oauth_marketplace_publishing_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/org-admin/developer-portal/oauth-marketplace-publishing/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["public_oauth_developer_portal_ready"] is True
    assert payload["blockers"] == []


def test_submit_oauth_marketplace_publishing_requires_approved_app(
    api_client: TestClient,
    admin_headers: dict[str, str],
    oauth_marketplace_publishing_env: None,
) -> None:
    create = api_client.post(
        "/api/v1/org-admin/developer-portal/oauth-apps",
        headers=admin_headers,
        json={
            "name": "Pending Marketplace App",
            "redirect_uri": "https://example.test/callback",
            "scopes": ["read"],
        },
    )
    assert create.status_code == 201, create.text
    app_id = create.json()["id"]

    response = api_client.post(
        f"/api/v1/org-admin/developer-portal/oauth-marketplace-publishing/oauth-apps/{app_id}/start",
        headers=admin_headers,
        json={
            "publishing_summary": "Attempt marketplace publish before app approved",
            "marketplace_listing_slug": "pending-partner-app",
        },
    )
    assert response.status_code == 409
    assert "not approved" in response.json()["detail"]


def test_submit_and_approve_oauth_marketplace_publishing_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    oauth_marketplace_publishing_env: None,
) -> None:
    app_id = _prepare_approved_oauth_developer_app(api_client, admin_headers)

    submit = api_client.post(
        f"/api/v1/org-admin/developer-portal/oauth-marketplace-publishing/oauth-apps/{app_id}/start",
        headers=admin_headers,
        json={
            "publishing_summary": "Marketplace listing after approved OAuth app",
            "marketplace_listing_slug": "partner-crm-app",
        },
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["oauth_developer_app_id"] == app_id
    assert run["marketplace_listing_slug"] == "partner-crm-app"

    approve = api_client.post(
        f"/api/v1/org-admin/developer-portal/oauth-marketplace-publishing/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()["run"]
    assert approved["status"] == "approved"
    assert approved["approved_at"] is not None


def test_submit_oauth_marketplace_publishing_unknown_app(
    api_client: TestClient,
    admin_headers: dict[str, str],
    oauth_marketplace_publishing_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/org-admin/developer-portal/oauth-marketplace-publishing/oauth-apps/{uuid.uuid4()}/start",
        headers=admin_headers,
        json={
            "publishing_summary": "Missing OAuth developer app",
            "marketplace_listing_slug": "missing-app",
        },
    )
    assert response.status_code == 404


def test_submit_oauth_marketplace_publishing_forbidden_for_manager(
    api_client: TestClient,
    admin_headers: dict[str, str],
    manager_headers: dict[str, str],
    oauth_marketplace_publishing_env: None,
) -> None:
    app_id = _prepare_approved_oauth_developer_app(api_client, admin_headers)
    response = api_client.post(
        f"/api/v1/org-admin/developer-portal/oauth-marketplace-publishing/oauth-apps/{app_id}/start",
        headers=manager_headers,
        json={
            "publishing_summary": "Should not submit",
            "marketplace_listing_slug": "forbidden",
        },
    )
    assert response.status_code == 403


def test_list_oauth_marketplace_publishing_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    oauth_marketplace_publishing_env: None,
) -> None:
    app_id = _prepare_approved_oauth_developer_app(api_client, admin_headers)
    api_client.post(
        f"/api/v1/org-admin/developer-portal/oauth-marketplace-publishing/oauth-apps/{app_id}/start",
        headers=admin_headers,
        json={
            "publishing_summary": "Listing test OAuth marketplace publishing run",
            "marketplace_listing_slug": "listing-test",
        },
    )

    listing = api_client.get(
        "/api/v1/org-admin/developer-portal/oauth-marketplace-publishing/runs",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
