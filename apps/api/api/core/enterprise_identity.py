"""Enterprise identity configuration and readiness gates."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.core.feature_flags import FeatureFlag, is_feature_enabled


class SsoProvider(StrEnum):
    NONE = "none"
    OIDC = "oidc"
    SAML = "saml"


class MfaMode(StrEnum):
    NONE = "none"
    TOTP = "totp"


class EnterpriseFeatureDisabledError(Exception):
    def __init__(self) -> None:
        super().__init__("Enterprise features are disabled (ENABLE_ENTERPRISE=false)")


class EnterpriseIdentityNotReadyError(Exception):
    def __init__(self, blockers: list[str]) -> None:
        self.blockers = blockers
        super().__init__("Enterprise identity is not ready")


class EnterpriseIdentitySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    enterprise_sso_provider: SsoProvider = Field(default=SsoProvider.NONE)
    enterprise_sso_issuer_url: str | None = None
    enterprise_sso_client_id: str | None = None
    enterprise_sso_client_secret: str | None = None
    enterprise_mfa_mode: MfaMode = Field(default=MfaMode.NONE)
    enterprise_mfa_issuer: str | None = Field(
        default=None,
        description="Display name shown in authenticator apps for TOTP enrollment",
    )


@dataclass(frozen=True, slots=True)
class EnterpriseIdentityStatus:
    feature_enabled: bool
    sso_provider: str
    sso_ready: bool
    mfa_mode: str
    mfa_ready: bool
    ready: bool
    blockers: tuple[str, ...]


@lru_cache
def get_enterprise_identity_settings() -> EnterpriseIdentitySettings:
    return EnterpriseIdentitySettings()


def evaluate_enterprise_identity_status(
    settings: EnterpriseIdentitySettings | None = None,
    *,
    feature_enabled: bool | None = None,
) -> EnterpriseIdentityStatus:
    current = settings or get_enterprise_identity_settings()
    enabled = (
        is_feature_enabled(FeatureFlag.ENABLE_ENTERPRISE)
        if feature_enabled is None
        else feature_enabled
    )
    blockers: list[str] = []

    if not enabled:
        blockers.append("ENABLE_ENTERPRISE is false")

    sso_ready = False
    if current.enterprise_sso_provider is not SsoProvider.NONE:
        if not current.enterprise_sso_issuer_url:
            blockers.append("ENTERPRISE_SSO_ISSUER_URL is not configured")
        if not current.enterprise_sso_client_id:
            blockers.append("ENTERPRISE_SSO_CLIENT_ID is not configured")
        if current.enterprise_sso_provider is SsoProvider.OIDC:
            if not current.enterprise_sso_client_secret:
                blockers.append("ENTERPRISE_SSO_CLIENT_SECRET is not configured for oidc")
        sso_ready = not any(blocker.startswith("ENTERPRISE_SSO_") for blocker in blockers)

    mfa_ready = False
    if current.enterprise_mfa_mode is MfaMode.TOTP:
        if not current.enterprise_mfa_issuer:
            blockers.append("ENTERPRISE_MFA_ISSUER is not configured for totp MFA")
        else:
            mfa_ready = True

    if (
        enabled
        and not sso_ready
        and not mfa_ready
        and current.enterprise_sso_provider is SsoProvider.NONE
        and current.enterprise_mfa_mode is MfaMode.NONE
    ):
        blockers.append("Configure SSO provider or MFA mode for enterprise identity")

    ready = enabled and (sso_ready or mfa_ready)

    return EnterpriseIdentityStatus(
        feature_enabled=enabled,
        sso_provider=current.enterprise_sso_provider.value,
        sso_ready=sso_ready,
        mfa_mode=current.enterprise_mfa_mode.value,
        mfa_ready=mfa_ready,
        ready=ready,
        blockers=tuple(blockers),
    )


def require_enterprise_identity_ready(
    settings: EnterpriseIdentitySettings | None = None,
    *,
    require_sso: bool = False,
    require_mfa: bool = False,
) -> EnterpriseIdentityStatus:
    status = evaluate_enterprise_identity_status(settings)
    if not status.feature_enabled:
        raise EnterpriseFeatureDisabledError()
    if require_sso and not status.sso_ready:
        raise EnterpriseIdentityNotReadyError(list(status.blockers))
    if require_mfa and not status.mfa_ready:
        raise EnterpriseIdentityNotReadyError(list(status.blockers))
    if not status.ready:
        raise EnterpriseIdentityNotReadyError(list(status.blockers))
    return status
