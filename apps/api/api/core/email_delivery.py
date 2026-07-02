"""Email delivery scaffold gate helpers.

This module intentionally does not send emails yet. It only evaluates
configuration readiness for future provider wiring.
"""

from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.core.feature_flags import FeatureFlag, is_feature_enabled


class EmailProvider(StrEnum):
    NONE = "none"
    SMTP = "smtp"
    SENDGRID = "sendgrid"


class EmailDeliverySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    email_provider: EmailProvider = Field(default=EmailProvider.NONE)
    email_from_address: str | None = None
    email_smtp_host: str | None = None
    email_smtp_port: int = 587
    email_sendgrid_api_key: str | None = None


class EmailDeliveryStatus:
    def __init__(
        self,
        *,
        enabled: bool,
        ready: bool,
        provider: str,
        from_address: str | None,
        blockers: list[str],
    ) -> None:
        self.enabled = enabled
        self.ready = ready
        self.provider = provider
        self.from_address = from_address
        self.blockers = blockers


@lru_cache
def get_email_delivery_settings() -> EmailDeliverySettings:
    return EmailDeliverySettings()


def get_email_delivery_status(settings: EmailDeliverySettings | None = None) -> EmailDeliveryStatus:
    feature_enabled = is_feature_enabled(FeatureFlag.ENABLE_EMAIL_DELIVERY)
    current = settings or get_email_delivery_settings()
    blockers: list[str] = []

    if not feature_enabled:
        blockers.append("ENABLE_EMAIL_DELIVERY is false")

    if current.email_provider == EmailProvider.NONE:
        blockers.append("EMAIL_PROVIDER is not configured")

    if not current.email_from_address:
        blockers.append("EMAIL_FROM_ADDRESS is not configured")

    if current.email_provider == EmailProvider.SMTP and not current.email_smtp_host:
        blockers.append("EMAIL_SMTP_HOST is not configured for smtp provider")

    if current.email_provider == EmailProvider.SENDGRID and not current.email_sendgrid_api_key:
        blockers.append("EMAIL_SENDGRID_API_KEY is not configured for sendgrid provider")

    return EmailDeliveryStatus(
        enabled=feature_enabled,
        ready=len(blockers) == 0,
        provider=current.email_provider.value,
        from_address=current.email_from_address,
        blockers=blockers,
    )
