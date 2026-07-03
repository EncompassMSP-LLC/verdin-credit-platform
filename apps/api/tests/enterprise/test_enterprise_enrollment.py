"""Enterprise identity enrollment integration tests."""

from unittest.mock import AsyncMock

import pyotp
import pytest
from fastapi.testclient import TestClient

from api.core.enterprise_oidc import OidcDiscoveryDocument, OidcTokenResponse, OidcUserInfo
from api.modules.auth.models import User


def test_totp_enrollment_flow(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_manager_user: User,
    enterprise_totp_env: None,
) -> None:
    start = api_client.post("/api/v1/enterprise/mfa/totp/enroll", headers=manager_headers)
    assert start.status_code == 201, start.text
    payload = start.json()
    assert payload["secret"]
    assert payload["otpauth_url"].startswith("otpauth://")
    assert payload["issuer"] == "Verdin Credit Platform"

    code = pyotp.TOTP(payload["secret"]).now()
    confirm = api_client.post(
        "/api/v1/enterprise/mfa/totp/confirm",
        headers=manager_headers,
        json={"code": code},
    )
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()["enrolled"] is True

    status_response = api_client.get("/api/v1/enterprise/mfa/totp", headers=manager_headers)
    assert status_response.status_code == 200
    assert status_response.json()["enrolled"] is True

    disable = api_client.delete("/api/v1/enterprise/mfa/totp", headers=manager_headers)
    assert disable.status_code == 200
    assert disable.json()["enrolled"] is False


def test_totp_enrollment_hidden_when_enterprise_disabled(
    api_client: TestClient,
    manager_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from api.core.enterprise_identity import get_enterprise_identity_settings
    from api.core.feature_flags import get_feature_flags

    monkeypatch.setenv("ENABLE_ENTERPRISE", "false")
    get_feature_flags.cache_clear()
    get_enterprise_identity_settings.cache_clear()

    response = api_client.post("/api/v1/enterprise/mfa/totp/enroll", headers=manager_headers)
    assert response.status_code == 404


def test_totp_confirm_rejects_invalid_code(
    api_client: TestClient,
    manager_headers: dict[str, str],
    enterprise_totp_env: None,
) -> None:
    start = api_client.post("/api/v1/enterprise/mfa/totp/enroll", headers=manager_headers)
    assert start.status_code == 201

    confirm = api_client.post(
        "/api/v1/enterprise/mfa/totp/confirm",
        headers=manager_headers,
        json={"code": "000000"},
    )
    assert confirm.status_code == 400


def test_sso_enrollment_flow(
    api_client: TestClient,
    manager_headers: dict[str, str],
    case_manager_user: User,
    enterprise_oidc_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    discovery = OidcDiscoveryDocument(
        authorization_endpoint="https://idp.example.com/authorize",
        token_endpoint="https://idp.example.com/token",
        userinfo_endpoint="https://idp.example.com/userinfo",
    )
    monkeypatch.setattr(
        "api.modules.enterprise.service.fetch_oidc_discovery",
        AsyncMock(return_value=discovery),
    )
    monkeypatch.setattr(
        "api.modules.enterprise.service.exchange_oidc_authorization_code",
        AsyncMock(
            return_value=OidcTokenResponse(
                access_token="access", id_token=None, token_type="Bearer"
            )
        ),
    )
    monkeypatch.setattr(
        "api.modules.enterprise.service.fetch_oidc_userinfo",
        AsyncMock(
            return_value=OidcUserInfo(subject="idp-subject-1", email=case_manager_user.email)
        ),
    )

    start = api_client.post("/api/v1/enterprise/sso/enrollment/start", headers=manager_headers)
    assert start.status_code == 201, start.text
    start_payload = start.json()
    assert start_payload["provider"] == "oidc"
    assert "authorize" in start_payload["authorization_url"]
    assert start_payload["state"]

    complete = api_client.post(
        "/api/v1/enterprise/sso/enrollment/complete",
        headers=manager_headers,
        json={"code": "auth-code", "state": start_payload["state"]},
    )
    assert complete.status_code == 200, complete.text
    complete_payload = complete.json()
    assert complete_payload["linked"] is True
    assert complete_payload["idp_subject"] == "idp-subject-1"

    status_response = api_client.get("/api/v1/enterprise/sso/enrollment", headers=manager_headers)
    assert status_response.status_code == 200
    assert status_response.json()["linked"] is True


def test_sso_enrollment_rejects_mismatched_state(
    api_client: TestClient,
    manager_headers: dict[str, str],
    enterprise_oidc_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import uuid

    from api.core.enterprise_oidc import create_sso_enrollment_state

    start = api_client.post("/api/v1/enterprise/sso/enrollment/start", headers=manager_headers)
    assert start.status_code == 201

    bad_state = create_sso_enrollment_state(uuid.uuid4())
    response = api_client.post(
        "/api/v1/enterprise/sso/enrollment/complete",
        headers=manager_headers,
        json={"code": "auth-code", "state": bad_state},
    )
    assert response.status_code == 403
