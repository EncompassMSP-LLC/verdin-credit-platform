"""Public OAuth developer portal scaffold tests."""

from fastapi.testclient import TestClient


def test_public_oauth_portal_hidden_when_disabled(
    api_client: TestClient,
    admin_headers: dict[str, str],
    enterprise_enabled: None,
) -> None:
    response = api_client.get(
        "/api/v1/org-admin/developer-portal/oauth-apps", headers=admin_headers
    )
    assert response.status_code == 404


def test_create_list_and_approve_public_oauth_app(
    api_client: TestClient,
    admin_headers: dict[str, str],
    public_oauth_portal_env: None,
) -> None:
    create = api_client.post(
        "/api/v1/org-admin/developer-portal/oauth-apps",
        headers=admin_headers,
        json={
            "name": "Partner CRM App",
            "redirect_uri": "https://example.partner.test/oauth/callback",
            "scopes": ["read", "write"],
        },
    )
    assert create.status_code == 201, create.text
    created = create.json()
    assert created["status"] == "pending_approval"
    assert created["requested_at"] is not None

    listing = api_client.get("/api/v1/org-admin/developer-portal/oauth-apps", headers=admin_headers)
    assert listing.status_code == 200, listing.text
    assert listing.json()[0]["id"] == created["id"]

    approve = api_client.post(
        f"/api/v1/org-admin/developer-portal/oauth-apps/{created['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200, approve.text
    approved = approve.json()
    assert approved["status"] == "approved"
    assert approved["approved_at"] is not None


def test_public_oauth_portal_forbidden_for_manager(
    api_client: TestClient,
    manager_headers: dict[str, str],
    public_oauth_portal_env: None,
) -> None:
    create = api_client.post(
        "/api/v1/org-admin/developer-portal/oauth-apps",
        headers=manager_headers,
        json={
            "name": "Manager App",
            "redirect_uri": "https://example.test/callback",
            "scopes": ["read"],
        },
    )
    assert create.status_code == 403
