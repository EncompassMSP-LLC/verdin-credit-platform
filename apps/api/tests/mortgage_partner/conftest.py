"""Fixtures for mortgage partner tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

import api.models  # noqa: F401 — register ORM mappers
from api.core.audit import apply_audit_on_create
from api.core.constants import UserRole
from api.core.feature_flags import get_feature_flags
from api.core.security import hash_password
from api.modules.auth.models import Organization, User
from api.modules.clients.models import Client, ClientStatus


@pytest.fixture
def mortgage_partner_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_MORTGAGE_PARTNER", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
def mortgage_partner_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_MORTGAGE_PARTNER", "false")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
async def cro_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="CRO Test Org",
        slug=f"cro-{uuid.uuid4().hex[:8]}",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    return org


@pytest.fixture
async def partner_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Lender Partner Org",
        slug=f"lender-{uuid.uuid4().hex[:8]}",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    return org


@pytest.fixture
async def other_cro_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Other CRO Org",
        slug=f"other-cro-{uuid.uuid4().hex[:8]}",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    return org


@pytest.fixture
async def admin_user(db_session: AsyncSession, cro_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"mp-admin-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Mortgage",
        last_name="Admin",
        role=UserRole.ADMIN,
        organization_id=cro_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def case_manager_user(db_session: AsyncSession, cro_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"mp-cm-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Case",
        last_name="Manager",
        role=UserRole.CASE_MANAGER,
        organization_id=cro_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def other_admin_user(db_session: AsyncSession, other_cro_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"mp-other-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Other",
        last_name="Admin",
        role=UserRole.ADMIN,
        organization_id=other_cro_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def partner_lo_user(db_session: AsyncSession, partner_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"mp-lo-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Loan",
        last_name="Officer",
        role=UserRole.READ_ONLY,
        organization_id=partner_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def client_record(
    db_session: AsyncSession, cro_org: Organization, admin_user: User
) -> Client:
    client = Client(
        id=uuid.uuid4(),
        organization_id=cro_org.id,
        display_name="Referral Borrower",
        email="borrower@test.example",
        status=ClientStatus.ACTIVE,
    )
    apply_audit_on_create(client, admin_user.id)
    db_session.add(client)
    await db_session.commit()
    return client


def _login(api_client: TestClient, email: str, password: str = "password123") -> dict[str, str]:
    response = api_client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(api_client: TestClient, admin_user: User) -> dict[str, str]:
    return _login(api_client, admin_user.email)


@pytest.fixture
def case_manager_headers(api_client: TestClient, case_manager_user: User) -> dict[str, str]:
    return _login(api_client, case_manager_user.email)


@pytest.fixture
def other_admin_headers(api_client: TestClient, other_admin_user: User) -> dict[str, str]:
    return _login(api_client, other_admin_user.email)
