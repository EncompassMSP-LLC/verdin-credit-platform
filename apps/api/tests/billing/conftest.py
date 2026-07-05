"""Billing test fixtures."""

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
def enterprise_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_ENTERPRISE", "true")
    get_feature_flags.cache_clear()
    yield
    get_feature_flags.cache_clear()


@pytest.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name="Billing Test Organization",
        slug=f"billing-org-{uuid.uuid4().hex[:8]}",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    return org


@pytest.fixture
async def admin_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"billing-admin-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Billing",
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
        email=f"billing-mgr-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Billing",
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
async def read_only_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"billing-readonly-{uuid.uuid4().hex[:8]}@test.example",
        hashed_password=hash_password("password123"),
        first_name="Billing",
        last_name="Reader",
        role=UserRole.READ_ONLY,
        organization_id=test_org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
def billing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_BILLING", "true")
    monkeypatch.setenv("ENABLE_ENTERPRISE", "true")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_example")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    monkeypatch.setenv("STRIPE_DEFAULT_PRICE_ID", "price_test_default")
    from api.core.stripe_billing import get_stripe_billing_settings

    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()


@pytest.fixture
def invoicing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_BILLING", "true")
    monkeypatch.setenv("ENABLE_BILLING_INVOICING", "true")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_example")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    monkeypatch.setenv("STRIPE_DEFAULT_PRICE_ID", "price_test_default")
    from api.core.stripe_billing import get_stripe_billing_settings

    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()


@pytest.fixture
def manager_headers(api_client: TestClient, case_manager_user: User) -> dict[str, str]:
    return _login(api_client, case_manager_user.email)


@pytest.fixture
def readonly_headers(api_client: TestClient, read_only_user: User) -> dict[str, str]:
    return _login(api_client, read_only_user.email)


@pytest.fixture
def collection_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_BILLING", "true")
    monkeypatch.setenv("ENABLE_ENTERPRISE", "true")
    monkeypatch.setenv("ENABLE_BILLING_INVOICING", "true")
    monkeypatch.setenv("ENABLE_BILLING_INVOICE_COLLECTION", "true")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_example")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    monkeypatch.setenv("STRIPE_DEFAULT_PRICE_ID", "price_test_default")
    from api.core.stripe_billing import get_stripe_billing_settings

    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()


@pytest.fixture
def stripe_invoice_pdf_env(monkeypatch: pytest.MonkeyPatch, collection_env: None) -> None:
    monkeypatch.setenv("ENABLE_STRIPE_INVOICE_PDF", "true")
    from api.core.stripe_billing import get_stripe_billing_settings

    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()


@pytest.fixture
def stripe_tax_calculation_env(
    monkeypatch: pytest.MonkeyPatch,
    stripe_invoice_pdf_env: None,
) -> None:
    monkeypatch.setenv("ENABLE_STRIPE_TAX_CALCULATION", "true")
    from api.core.stripe_billing import get_stripe_billing_settings

    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()
    yield
    get_feature_flags.cache_clear()
    get_stripe_billing_settings.cache_clear()
