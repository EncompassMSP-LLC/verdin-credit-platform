"""Enterprise identity scaffold tests."""

import pytest
from fastapi.testclient import TestClient

from api.core.enterprise import get_enterprise_identity_gate_status, require_enterprise_gateway
from api.core.enterprise_identity import (
    EnterpriseFeatureDisabledError,
    EnterpriseIdentityNotReadyError,
    EnterpriseIdentitySettings,
    SsoProvider,
    evaluate_enterprise_identity_status,
    get_enterprise_identity_settings,
)
from api.core.feature_flags import get_feature_flags


def test_evaluate_enterprise_identity_blocked_when_disabled() -> None:
    settings = EnterpriseIdentitySettings(
        enterprise_sso_provider=SsoProvider.OIDC,
        enterprise_sso_issuer_url="https://idp.example.com",
        enterprise_sso_client_id="client",
        enterprise_sso_client_secret="secret",
        enterprise_sso_redirect_uri="https://app.verdin.example/auth/sso/callback",
    )
    status = evaluate_enterprise_identity_status(settings, feature_enabled=False)
    assert status.ready is False
    assert "ENABLE_ENTERPRISE is false" in status.blockers


def test_evaluate_enterprise_identity_oidc_ready() -> None:
    settings = EnterpriseIdentitySettings(
        enterprise_sso_provider=SsoProvider.OIDC,
        enterprise_sso_issuer_url="https://idp.example.com",
        enterprise_sso_client_id="client",
        enterprise_sso_client_secret="secret",
        enterprise_sso_redirect_uri="https://app.verdin.example/auth/sso/callback",
    )
    status = evaluate_enterprise_identity_status(settings, feature_enabled=True)
    assert status.ready is True
    assert status.sso_ready is True
    assert status.blockers == ()


def test_require_enterprise_gateway_raises_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_ENTERPRISE", "false")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()
    with pytest.raises(EnterpriseFeatureDisabledError):
        require_enterprise_gateway()
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()


def test_require_enterprise_gateway_requires_sso_when_requested(
    enterprise_totp_env: None,
) -> None:
    with pytest.raises(EnterpriseIdentityNotReadyError):
        require_enterprise_gateway(require_sso=True)


def test_get_enterprise_status_endpoint_oidc_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    enterprise_oidc_env: None,
) -> None:
    response = api_client.get("/api/v1/enterprise/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["ready"] is True
    assert payload["sso_provider"] == "oidc"
    assert payload["sso_ready"] is True
    assert payload["blockers"] == []


def test_get_enterprise_status_endpoint_totp_ready(
    api_client: TestClient,
    manager_headers: dict[str, str],
    enterprise_totp_env: None,
) -> None:
    response = api_client.get("/api/v1/enterprise/status", headers=manager_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["ready"] is True
    assert payload["mfa_mode"] == "totp"
    assert payload["mfa_ready"] is True


def test_get_enterprise_status_requires_auth(
    api_client: TestClient,
    enterprise_oidc_env: None,
) -> None:
    response = api_client.get("/api/v1/enterprise/status")
    assert response.status_code == 401


def test_api_wrapper_matches_gate_status(enterprise_oidc_env: None) -> None:
    status = get_enterprise_identity_gate_status()
    assert status.ready is True
    require_enterprise_gateway()
