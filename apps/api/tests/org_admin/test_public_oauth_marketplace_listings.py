"""Admin-gated public OAuth marketplace listing integration tests."""

import uuid

from fastapi.testclient import TestClient

from tests.org_admin.test_oauth_marketplace_publishing import _prepare_approved_oauth_developer_app


def _prepare_approved_oauth_marketplace_publishing_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
) -> tuple[str, str]:
    app_id = _prepare_approved_oauth_developer_app(api_client, admin_headers)
    submit = api_client.post(
        f"/api/v1/org-admin/developer-portal/oauth-marketplace-publishing/oauth-apps/{app_id}/start",
        headers=admin_headers,
        json={
            "publishing_summary": "Parent marketplace publishing for public listing",
            "marketplace_listing_slug": "public-listing-parent",
        },
    )
    assert submit.status_code == 200, submit.text
    run_id = submit.json()["run"]["id"]
    approve = api_client.post(
        f"/api/v1/org-admin/developer-portal/oauth-marketplace-publishing/runs/{run_id}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["run"]["status"] == "approved"
    return app_id, run_id


def test_public_oauth_marketplace_listings_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    oauth_marketplace_publishing_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/org-admin/developer-portal/public-oauth-marketplace-listings/status",
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_public_oauth_marketplace_listings_status_ready(
    api_client: TestClient,
    admin_headers: dict[str, str],
    public_oauth_marketplace_listings_env: None,
) -> None:
    response = api_client.get(
        "/api/v1/org-admin/developer-portal/public-oauth-marketplace-listings/status",
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["ready"] is True
    assert payload["oauth_marketplace_publishing_ready"] is True
    assert payload["blockers"] == []


def test_submit_public_listing_requires_approved_publishing_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    public_oauth_marketplace_listings_env: None,
) -> None:
    app_id = _prepare_approved_oauth_developer_app(api_client, admin_headers)
    submit_parent = api_client.post(
        f"/api/v1/org-admin/developer-portal/oauth-marketplace-publishing/oauth-apps/{app_id}/start",
        headers=admin_headers,
        json={
            "publishing_summary": "Pending — cannot start public listing yet",
            "marketplace_listing_slug": "pending-public-listing",
        },
    )
    assert submit_parent.status_code == 200, submit_parent.text
    pending_run_id = submit_parent.json()["run"]["id"]

    response = api_client.post(
        f"/api/v1/org-admin/developer-portal/public-oauth-marketplace-listings/publishing-runs/{pending_run_id}/start",
        headers=admin_headers,
        json={"listing_summary": "Attempt public listing before publishing approved"},
    )
    assert response.status_code == 409
    assert "not approved" in response.json()["detail"]


def test_submit_and_approve_public_oauth_marketplace_listing_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    public_oauth_marketplace_listings_env: None,
) -> None:
    app_id, publishing_run_id = _prepare_approved_oauth_marketplace_publishing_run(
        api_client, admin_headers
    )

    submit = api_client.post(
        f"/api/v1/org-admin/developer-portal/public-oauth-marketplace-listings/publishing-runs/{publishing_run_id}/start",
        headers=admin_headers,
        json={
            "listing_summary": "Public marketplace listing after approved publishing",
            "public_listing_url": "https://marketplace.example.test/apps/public-listing-parent",
        },
    )
    assert submit.status_code == 200, submit.text
    run = submit.json()["run"]
    assert run["status"] == "pending_approval"
    assert run["oauth_marketplace_publishing_run_id"] == publishing_run_id
    assert run["oauth_developer_app_id"] == app_id
    assert run["marketplace_listing_slug"] == "public-listing-parent"

    approve = api_client.post(
        f"/api/v1/org-admin/developer-portal/public-oauth-marketplace-listings/runs/{run['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    listed = approve.json()["run"]
    assert listed["status"] == "listed"
    assert listed["listed_at"] is not None
    assert listed["approved_at"] is not None


def test_submit_public_listing_unknown_publishing_run(
    api_client: TestClient,
    admin_headers: dict[str, str],
    public_oauth_marketplace_listings_env: None,
) -> None:
    response = api_client.post(
        f"/api/v1/org-admin/developer-portal/public-oauth-marketplace-listings/publishing-runs/{uuid.uuid4()}/start",
        headers=admin_headers,
        json={"listing_summary": "Missing OAuth marketplace publishing run"},
    )
    assert response.status_code == 404


def test_submit_public_listing_forbidden_for_manager(
    api_client: TestClient,
    admin_headers: dict[str, str],
    manager_headers: dict[str, str],
    public_oauth_marketplace_listings_env: None,
) -> None:
    _, publishing_run_id = _prepare_approved_oauth_marketplace_publishing_run(
        api_client, admin_headers
    )
    response = api_client.post(
        f"/api/v1/org-admin/developer-portal/public-oauth-marketplace-listings/publishing-runs/{publishing_run_id}/start",
        headers=manager_headers,
        json={"listing_summary": "Should not submit"},
    )
    assert response.status_code == 403


def test_list_public_oauth_marketplace_listing_runs(
    api_client: TestClient,
    admin_headers: dict[str, str],
    public_oauth_marketplace_listings_env: None,
) -> None:
    _, publishing_run_id = _prepare_approved_oauth_marketplace_publishing_run(
        api_client, admin_headers
    )
    api_client.post(
        f"/api/v1/org-admin/developer-portal/public-oauth-marketplace-listings/publishing-runs/{publishing_run_id}/start",
        headers=admin_headers,
        json={"listing_summary": "List test public OAuth marketplace listing run"},
    )

    listing = api_client.get(
        "/api/v1/org-admin/developer-portal/public-oauth-marketplace-listings/runs",
        headers=admin_headers,
    )
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] >= 1
