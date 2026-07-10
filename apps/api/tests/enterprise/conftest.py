"""Fixtures for enterprise identity tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

import api.models  # noqa: F401 — register all ORM mappers
from api.core.constants import UserRole
from api.core.enterprise_identity import get_enterprise_identity_settings
from api.core.feature_flags import get_feature_flags
from api.core.security import hash_password
from api.modules.auth.models import Organization, User


@pytest.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Test Organization",
        slug=f"test-org-{uuid.uuid4().hex[:8]}",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    return org


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


def _login(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


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
def admin_headers(api_client: TestClient, admin_user: User) -> dict[str, str]:
    return _login(api_client, admin_user.email)


@pytest.fixture
def readonly_headers(api_client: TestClient, read_only_user: User) -> dict[str, str]:
    return _login(api_client, read_only_user.email)


@pytest.fixture
def manager_headers(api_client: TestClient, case_manager_user: User) -> dict[str, str]:
    return _login(api_client, case_manager_user.email)


@pytest.fixture
def enterprise_oidc_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_ENTERPRISE", "true")
    monkeypatch.setenv("ENTERPRISE_SSO_PROVIDER", "oidc")
    monkeypatch.setenv("ENTERPRISE_SSO_ISSUER_URL", "https://idp.example.com")
    monkeypatch.setenv("ENTERPRISE_SSO_CLIENT_ID", "verdin-client")
    monkeypatch.setenv("ENTERPRISE_SSO_CLIENT_SECRET", "secret")
    monkeypatch.setenv(
        "ENTERPRISE_SSO_REDIRECT_URI",
        "https://app.verdin.example/auth/sso/callback",
    )
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


@pytest.fixture
def federation_env(monkeypatch: pytest.MonkeyPatch, enterprise_oidc_env: None) -> None:
    monkeypatch.setenv("ENABLE_IDP_FEDERATION", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


VALID_SAML_METADATA = """<?xml version="1.0"?>
<EntityDescriptor entityID="https://idp.example.com/metadata"
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"/>
</EntityDescriptor>"""


@pytest.fixture
def saml_metadata_only_env(
    monkeypatch: pytest.MonkeyPatch,
    federation_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_SAML_FEDERATION_METADATA", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


@pytest.fixture
def hris_sync_env(
    monkeypatch: pytest.MonkeyPatch,
    federation_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_SAML_FEDERATION_METADATA", "true")
    monkeypatch.setenv("ENABLE_HRIS_BIDIRECTIONAL_SYNC", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


@pytest.fixture
def saml_cert_rotation_env(
    monkeypatch: pytest.MonkeyPatch,
    hris_sync_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_SAML_CERTIFICATE_ROTATION", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


@pytest.fixture
def saml_automated_rotation_env(
    monkeypatch: pytest.MonkeyPatch,
    saml_cert_rotation_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_SAML_AUTOMATED_ROTATION", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


@pytest.fixture
def saml_passwordless_enrollment_env(
    monkeypatch: pytest.MonkeyPatch,
    saml_automated_rotation_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_SAML_PASSWORDLESS_ENROLLMENT", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


@pytest.fixture
def hris_passwordless_ui_env(
    monkeypatch: pytest.MonkeyPatch,
    saml_passwordless_enrollment_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_HRIS_PASSWORDLESS_UI", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


@pytest.fixture
def mobile_passkey_readiness_env(
    monkeypatch: pytest.MonkeyPatch,
    hris_passwordless_ui_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_MOBILE_PASSKEY_READINESS", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


@pytest.fixture
def native_mobile_passkey_client_env(
    monkeypatch: pytest.MonkeyPatch,
    mobile_passkey_readiness_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_NATIVE_MOBILE_PASSKEY_CLIENT", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


@pytest.fixture
def bulk_idp_provisioning_env(
    monkeypatch: pytest.MonkeyPatch,
    hris_passwordless_ui_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_MULTI_IDP_BULK_PROVISIONING", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


@pytest.fixture
def hris_lifecycle_sync_env(
    monkeypatch: pytest.MonkeyPatch,
    hris_sync_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_HRIS_LIFECYCLE_SYNC", "true")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


@pytest.fixture
def enterprise_totp_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_ENTERPRISE", "true")
    monkeypatch.setenv("ENTERPRISE_MFA_MODE", "totp")
    monkeypatch.setenv("ENTERPRISE_MFA_ISSUER", "Ultimate Credit Repair LLC")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
