"""Fixtures for reporting integration tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

import api.models  # noqa: F401 — register all ORM mappers
from api.core.constants import UserRole
from api.core.feature_flags import get_feature_flags
from api.core.security import hash_password
from api.modules.auth.models import Organization, User


@pytest.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Reporting Test Organization",
        slug=f"report-org-{uuid.uuid4().hex[:8]}",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    return org


@pytest.fixture
async def admin_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"report-admin-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Report",
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
        email=f"report-mgr-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Report",
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
def enterprise_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_ENTERPRISE", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
def cross_org_benchmark_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_ENTERPRISE", "true")
    monkeypatch.setenv("ENABLE_CROSS_ORG_BENCHMARK_ANALYTICS", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
def unredacted_cross_org_benchmark_export_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_ENTERPRISE", "true")
    monkeypatch.setenv("ENABLE_CROSS_ORG_BENCHMARK_ANALYTICS", "true")
    monkeypatch.setenv("ENABLE_UNREDACTED_CROSS_ORG_BENCHMARK_EXPORT", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()
