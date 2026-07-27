"""Fixtures for organization context / production org mode tests (LRP-109)."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

import api.models  # noqa: F401
from api.core.config import get_settings
from api.core.constants import UserRole
from api.core.security import hash_password
from api.modules.auth.models import Organization, OrganizationType, User
from api.modules.org_context.models import OrganizationFeatureFlag, OrgDemoFeature


@pytest.fixture(autouse=True)
def _demo_env_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOW_DEMO_ORGS", "true")
    monkeypatch.setenv("ENABLE_SAMPLE_DATA", "true")
    monkeypatch.setenv("ENABLE_DEMO_LOGIN", "true")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
async def production_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Production Org",
        slug=f"prod-org-{uuid.uuid4().hex[:8]}",
        is_active=True,
        organization_type=OrganizationType.PRODUCTION,
    )
    db_session.add(org)
    await db_session.commit()
    return org


@pytest.fixture
async def demo_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Demo Org",
        slug=f"demo-org-{uuid.uuid4().hex[:8]}",
        is_active=True,
        organization_type=OrganizationType.DEMO,
    )
    db_session.add(org)
    await db_session.flush()
    for feature in (
        OrgDemoFeature.DEMO_DATA,
        OrgDemoFeature.SAMPLE_BORROWERS,
        OrgDemoFeature.FAKE_CREDIT_REPORTS,
        OrgDemoFeature.TRAINING_MODE,
    ):
        db_session.add(
            OrganizationFeatureFlag(
                id=uuid.uuid4(),
                organization_id=org.id,
                feature=feature,
                enabled=True,
            )
        )
    await db_session.commit()
    return org


@pytest.fixture
async def production_admin(db_session: AsyncSession, production_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"prod-admin-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Prod",
        last_name="Admin",
        role=UserRole.ADMIN,
        organization_id=production_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def demo_admin(db_session: AsyncSession, demo_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"demo-admin-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Demo",
        last_name="Admin",
        role=UserRole.ADMIN,
        organization_id=demo_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
def production_admin_headers(api_client: TestClient, production_admin: User) -> dict[str, str]:
    response = api_client.post(
        "/api/v1/auth/login",
        json={"email": production_admin.email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def demo_admin_headers(api_client: TestClient, demo_admin: User) -> dict[str, str]:
    response = api_client.post(
        "/api/v1/auth/login",
        json={"email": demo_admin.email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
