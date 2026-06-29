"""Security review tests for authentication behavior."""

import uuid
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.security import create_access_token, hash_password
from api.modules.auth.models import Organization, User


@pytest.fixture
async def auth_test_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Auth Security Organization",
        slug=f"auth-security-{uuid.uuid4().hex[:8]}",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    return org


@pytest.fixture
async def active_user(db_session: AsyncSession, auth_test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"active-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Active",
        last_name="User",
        role=UserRole.OWNER,
        organization_id=auth_test_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def inactive_user(db_session: AsyncSession, auth_test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"inactive-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Inactive",
        last_name="User",
        role=UserRole.OWNER,
        organization_id=auth_test_org.id,
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    return user


def test_login_succeeds_for_active_user(api_client: TestClient, active_user: User) -> None:
    response = api_client.post(
        "/api/v1/auth/login",
        json={"email": active_user.email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"]


def test_login_rejects_invalid_password(api_client: TestClient, active_user: User) -> None:
    response = api_client.post(
        "/api/v1/auth/login",
        json={"email": active_user.email, "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_rejects_inactive_user(api_client: TestClient, inactive_user: User) -> None:
    response = api_client.post(
        "/api/v1/auth/login",
        json={"email": inactive_user.email, "password": "password123"},
    )
    assert response.status_code == 403


def test_expired_access_token_is_rejected(api_client: TestClient, active_user: User) -> None:
    token = create_access_token(
        str(active_user.id),
        active_user.role,
        expires_delta=timedelta(seconds=-1),
    )
    response = api_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_invalid_token_handling_is_safe(api_client: TestClient) -> None:
    response = api_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_refresh_token_flow_rotates_refresh_token(
    api_client: TestClient,
    active_user: User,
) -> None:
    login = api_client.post(
        "/api/v1/auth/login",
        json={"email": active_user.email, "password": "password123"},
    )
    assert login.status_code == 200, login.text

    old_refresh = login.json()["refresh_token"]
    refresh = api_client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert refresh.status_code == 200, refresh.text
    assert refresh.json()["access_token"]
    assert refresh.json()["refresh_token"] != old_refresh
