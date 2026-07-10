"""API key authentication integration tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.api_keys import generate_api_key_material
from api.core.audit import apply_audit_on_create
from api.modules.auth.models import Organization, User
from api.modules.org_admin.models import ApiKeyScope, OrganizationApiKey
from api.modules.org_admin.repository import OrgAdminRepository
from tests.helpers.client_payload import sample_client_payload


@pytest.fixture
async def read_api_key(
    db_session: AsyncSession,
    test_org: Organization,
    admin_user: User,
) -> tuple[str, OrganizationApiKey]:
    full_key, key_prefix, key_hash = generate_api_key_material()
    api_key = OrganizationApiKey(
        organization_id=test_org.id,
        name="Integration read key",
        key_prefix=key_prefix,
        key_hash=key_hash,
        is_active=True,
    )
    api_key.set_scopes([ApiKeyScope.READ])
    apply_audit_on_create(api_key, admin_user.id)
    repo = OrgAdminRepository(db_session)
    await repo.create_api_key(api_key)
    await db_session.commit()
    return full_key, api_key


@pytest.fixture
async def write_only_api_key(
    db_session: AsyncSession,
    test_org: Organization,
    admin_user: User,
) -> str:
    full_key, key_prefix, key_hash = generate_api_key_material()
    api_key = OrganizationApiKey(
        organization_id=test_org.id,
        name="Write-only key",
        key_prefix=key_prefix,
        key_hash=key_hash,
        is_active=True,
    )
    api_key.set_scopes([ApiKeyScope.WRITE])
    apply_audit_on_create(api_key, admin_user.id)
    repo = OrgAdminRepository(db_session)
    await repo.create_api_key(api_key)
    await db_session.commit()
    return full_key


def test_api_key_auth_hidden_when_enterprise_disabled(
    api_client: TestClient,
    read_api_key: tuple[str, OrganizationApiKey],
    enterprise_disabled: None,
) -> None:
    full_key, _ = read_api_key
    response = api_client.get(
        "/api/v1/reporting/operations",
        headers={"X-API-Key": full_key},
    )
    assert response.status_code == 404


def test_api_key_authenticates_operations_reporting(
    api_client: TestClient,
    admin_headers: dict[str, str],
    read_api_key: tuple[str, OrganizationApiKey],
    enterprise_enabled: None,
) -> None:
    create_client = api_client.post(
        "/api/v1/clients",
        headers=admin_headers,
        json=sample_client_payload(display_name="API key reporting client"),
    )
    assert create_client.status_code == 201, create_client.text

    full_key, api_key = read_api_key
    response = api_client.get(
        "/api/v1/reporting/operations",
        headers={"Authorization": f"Bearer {full_key}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["operations"]["clients"]["total"] >= 1

    list_response = api_client.get("/api/v1/org-admin/api-keys", headers=admin_headers)
    assert list_response.status_code == 200, list_response.text
    listed = next(item for item in list_response.json() if item["id"] == str(api_key.id))
    assert listed["last_used_at"] is not None


def test_api_key_requires_read_scope_for_reporting(
    api_client: TestClient,
    write_only_api_key: str,
    enterprise_enabled: None,
) -> None:
    response = api_client.get(
        "/api/v1/reporting/operations",
        headers={"X-API-Key": write_only_api_key},
    )
    assert response.status_code == 403
    assert "read" in response.json()["detail"].lower()


def test_revoked_api_key_rejected(
    api_client: TestClient,
    admin_headers: dict[str, str],
    read_api_key: tuple[str, OrganizationApiKey],
    enterprise_enabled: None,
) -> None:
    full_key, api_key = read_api_key
    revoke = api_client.post(
        f"/api/v1/org-admin/api-keys/{api_key.id}/revoke",
        headers=admin_headers,
    )
    assert revoke.status_code == 200, revoke.text

    response = api_client.get(
        "/api/v1/reporting/operations",
        headers={"X-API-Key": full_key},
    )
    assert response.status_code == 401
