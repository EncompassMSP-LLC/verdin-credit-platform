"""Fixtures for organization admin tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

import api.models  # noqa: F401 — register all ORM mappers
from api.core.api_keys import generate_api_key_material
from api.core.audit import apply_audit_on_create
from api.core.constants import UserRole
from api.core.feature_flags import get_feature_flags
from api.core.security import hash_password
from api.modules.auth.models import Organization, User
from api.modules.org_admin.models import ApiKeyScope, OrganizationApiKey
from api.modules.org_admin.repository import OrgAdminRepository


@pytest.fixture
def enterprise_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_ENTERPRISE", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
def enterprise_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_ENTERPRISE", "false")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
def public_oauth_portal_env(
    monkeypatch: pytest.MonkeyPatch,
    enterprise_enabled: None,
) -> None:
    monkeypatch.setenv("ENABLE_API_DEVELOPER_PORTAL", "true")
    monkeypatch.setenv("ENABLE_PUBLIC_OAUTH_DEVELOPER_PORTAL", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
def oauth_marketplace_publishing_env(
    monkeypatch: pytest.MonkeyPatch,
    public_oauth_portal_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_OAUTH_MARKETPLACE_PUBLISHING", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Org Admin Test Organization",
        slug=f"org-admin-{uuid.uuid4().hex[:8]}",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    return org


@pytest.fixture
async def admin_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"org-admin-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Org",
        last_name="Admin",
        role=UserRole.ADMIN,
        organization_id=test_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def case_manager_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"org-mgr-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Org",
        last_name="Manager",
        role=UserRole.CASE_MANAGER,
        organization_id=test_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


def _login(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_headers(api_client: TestClient, admin_user: User) -> dict[str, str]:
    return _login(api_client, admin_user.email)


@pytest.fixture
def manager_headers(api_client: TestClient, case_manager_user: User) -> dict[str, str]:
    return _login(api_client, case_manager_user.email)


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
