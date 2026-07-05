"""Fixtures for compliance center integration tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

import api.models  # noqa: F401 — register all ORM mappers
from api.core.constants import UserRole
from api.core.feature_flags import get_feature_flags
from api.core.security import hash_password
from api.modules.auth.models import Organization, User
from api.modules.clients.models import Client, ClientStatus


@pytest.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Compliance Test Organization",
        slug=f"compliance-org-{uuid.uuid4().hex[:8]}",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    return org


@pytest.fixture
async def test_client(db_session: AsyncSession, test_org: Organization) -> Client:
    client = Client(
        id=uuid.uuid4(),
        organization_id=test_org.id,
        display_name="Compliance Test Client",
        email="client@compliance.test",
        status=ClientStatus.ACTIVE,
    )
    db_session.add(client)
    await db_session.commit()
    return client


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
    await db_session.commit()
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
    await db_session.commit()
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"admin-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Test",
        last_name="Admin",
        role=UserRole.ADMIN,
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
def manager_headers(api_client: TestClient, case_manager_user: User) -> dict[str, str]:
    return _login(api_client, case_manager_user.email)


@pytest.fixture
def readonly_headers(api_client: TestClient, read_only_user: User) -> dict[str, str]:
    return _login(api_client, read_only_user.email)


@pytest.fixture
def admin_headers(api_client: TestClient, admin_user: User) -> dict[str, str]:
    return _login(api_client, admin_user.email)


def sample_case_id(api_client: TestClient, manager_headers: dict[str, str]) -> str:
    response = api_client.post(
        "/api/v1/cases",
        headers=manager_headers,
        json={"title": "Dispute Filing Prep Case", "client_name": "Prep Client"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_account(api_client: TestClient, headers: dict[str, str], case_id: str) -> str:
    response = api_client.post(
        "/api/v1/accounts",
        headers=headers,
        json={
            "case_id": case_id,
            "creditor_name": "Example Bank",
            "bureau": "equifax",
            "account_type": "credit_card",
            "account_status": "open",
            "payment_status": "late_60",
            "account_number_masked": "****1234",
            "balance": "1500.00",
            "past_due_amount": "300.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.fixture
def dispute_filing_prep_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_AI", "true")
    monkeypatch.setenv("ENABLE_AGENT_OBSERVABILITY", "true")
    monkeypatch.setenv("ENABLE_AGENT_EXECUTION", "true")
    monkeypatch.setenv("ENABLE_DISPUTE_FILING_PREP", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
def dispute_bureau_submission_env(
    monkeypatch: pytest.MonkeyPatch,
    dispute_filing_prep_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_DISPUTE_BUREAU_SUBMISSION", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
def bureau_live_api_env(
    monkeypatch: pytest.MonkeyPatch,
    dispute_bureau_submission_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_BUREAU_LIVE_API", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
def autonomous_bureau_filing_env(
    monkeypatch: pytest.MonkeyPatch,
    bureau_live_api_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_AUTONOMOUS_BUREAU_FILING", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()
