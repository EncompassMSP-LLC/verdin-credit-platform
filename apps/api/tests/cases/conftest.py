"""Fixtures for case management integration tests."""

import uuid
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

import api.models  # noqa: F401 — register all ORM mappers
from api.core.constants import UserRole
from api.core.security import hash_password
from api.database.session import AsyncSessionLocal, get_db
from api.modules.auth.models import Organization, User
from main import app


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def api_client(db_session: AsyncSession) -> Generator[TestClient]:
    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Test Organization",
        slug=f"test-org-{uuid.uuid4().hex[:8]}",
        is_active=True,
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest.fixture
async def owner_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"owner-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Test",
        last_name="Owner",
        role=UserRole.OWNER,
        organization_id=test_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def case_manager_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"manager-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Test",
        last_name="Manager",
        role=UserRole.CASE_MANAGER,
        organization_id=test_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def read_only_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"readonly-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Test",
        last_name="Reader",
        role=UserRole.READ_ONLY,
        organization_id=test_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


def _login(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def auth_headers(api_client: TestClient, owner_user: User) -> dict[str, str]:
    return _login(api_client, owner_user.email)


@pytest.fixture
def manager_headers(api_client: TestClient, case_manager_user: User) -> dict[str, str]:
    return _login(api_client, case_manager_user.email)


@pytest.fixture
def readonly_headers(api_client: TestClient, read_only_user: User) -> dict[str, str]:
    return _login(api_client, read_only_user.email)
