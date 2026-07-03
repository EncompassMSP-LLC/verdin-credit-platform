"""OIDC enrollment helpers for enterprise SSO."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any
from urllib.parse import urlencode

import httpx
from jose import JWTError, jwt

from api.core.config import get_settings
from api.core.enterprise_identity import EnterpriseIdentitySettings, SsoProvider

SSO_ENROLLMENT_STATE_TYPE = "sso_enrollment_state"
SSO_ENROLLMENT_STATE_MINUTES = 10


@dataclass(frozen=True, slots=True)
class OidcDiscoveryDocument:
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str | None


@dataclass(frozen=True, slots=True)
class OidcTokenResponse:
    access_token: str
    id_token: str | None
    token_type: str


@dataclass(frozen=True, slots=True)
class OidcUserInfo:
    subject: str
    email: str | None


def create_sso_enrollment_state(user_id: uuid.UUID) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=SSO_ENROLLMENT_STATE_MINUTES)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": SSO_ENROLLMENT_STATE_TYPE,
        "exp": expire,
    }
    return str(jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm))


def decode_sso_enrollment_state(state: str) -> uuid.UUID:
    settings = get_settings()
    try:
        payload = jwt.decode(state, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise ValueError("Invalid SSO enrollment state") from exc
    if payload.get("type") != SSO_ENROLLMENT_STATE_TYPE:
        raise ValueError("Invalid SSO enrollment state type")
    user_id = payload.get("sub")
    if user_id is None:
        raise ValueError("SSO enrollment state missing subject")
    return uuid.UUID(str(user_id))


def build_oidc_authorization_url(
    settings: EnterpriseIdentitySettings,
    *,
    redirect_uri: str,
    state: str,
) -> str:
    if settings.enterprise_sso_provider is not SsoProvider.OIDC:
        raise ValueError("OIDC authorization requires oidc SSO provider")
    if not settings.enterprise_sso_issuer_url or not settings.enterprise_sso_client_id:
        raise ValueError("OIDC issuer URL and client ID are required")

    issuer = settings.enterprise_sso_issuer_url.rstrip("/")
    params = urlencode(
        {
            "client_id": settings.enterprise_sso_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid profile email",
            "state": state,
        },
    )
    return f"{issuer}/authorize?{params}"


@lru_cache
def _discovery_cache_key(issuer_url: str) -> str:
    return issuer_url.rstrip("/")


async def fetch_oidc_discovery(issuer_url: str) -> OidcDiscoveryDocument:
    issuer = issuer_url.rstrip("/")
    url = f"{issuer}/.well-known/openid-configuration"
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)
    if response.status_code >= 400:
        raise ValueError(f"OIDC discovery failed: {response.text}")
    data = response.json()
    return OidcDiscoveryDocument(
        authorization_endpoint=data["authorization_endpoint"],
        token_endpoint=data["token_endpoint"],
        userinfo_endpoint=data.get("userinfo_endpoint"),
    )


async def exchange_oidc_authorization_code(
    settings: EnterpriseIdentitySettings,
    *,
    code: str,
    redirect_uri: str,
    discovery: OidcDiscoveryDocument | None = None,
) -> OidcTokenResponse:
    if settings.enterprise_sso_provider is not SsoProvider.OIDC:
        raise ValueError("OIDC token exchange requires oidc SSO provider")
    if not settings.enterprise_sso_client_id or not settings.enterprise_sso_client_secret:
        raise ValueError("OIDC client credentials are required")

    doc = discovery
    if doc is None:
        if not settings.enterprise_sso_issuer_url:
            raise ValueError("OIDC issuer URL is required")
        doc = await fetch_oidc_discovery(settings.enterprise_sso_issuer_url)

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": settings.enterprise_sso_client_id,
        "client_secret": settings.enterprise_sso_client_secret,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(doc.token_endpoint, data=payload)
    if response.status_code >= 400:
        raise ValueError(f"OIDC token exchange failed: {response.text}")
    data = response.json()
    return OidcTokenResponse(
        access_token=data["access_token"],
        id_token=data.get("id_token"),
        token_type=data.get("token_type", "Bearer"),
    )


async def fetch_oidc_userinfo(
    discovery: OidcDiscoveryDocument,
    *,
    access_token: str,
) -> OidcUserInfo:
    if discovery.userinfo_endpoint is None:
        raise ValueError("OIDC userinfo endpoint is not available")
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            discovery.userinfo_endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if response.status_code >= 400:
        raise ValueError(f"OIDC userinfo failed: {response.text}")
    data = response.json()
    subject = data.get("sub")
    if not subject:
        raise ValueError("OIDC userinfo missing sub claim")
    return OidcUserInfo(subject=str(subject), email=data.get("email"))
