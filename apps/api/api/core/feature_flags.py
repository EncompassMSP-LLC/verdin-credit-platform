"""Feature flags loaded from environment variables."""

from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FeatureFlag(StrEnum):
    ENABLE_AI = "ENABLE_AI"
    ENABLE_LLM = "ENABLE_LLM"
    ENABLE_EMAIL_DELIVERY = "ENABLE_EMAIL_DELIVERY"
    ENABLE_IMPORTS = "ENABLE_IMPORTS"
    ENABLE_ENTERPRISE = "ENABLE_ENTERPRISE"
    ENABLE_BILLING = "ENABLE_BILLING"
    ENABLE_CLIENT_PORTAL = "ENABLE_CLIENT_PORTAL"


class FeatureFlags(BaseSettings):
    """Boolean feature toggles read from ``ENABLE_*`` environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    enable_ai: bool = Field(default=False, description="Enable AI-powered features")
    enable_llm: bool = Field(
        default=False,
        description="Enable external LLM provider calls (requires provider config)",
    )
    enable_email_delivery: bool = Field(
        default=False,
        description="Enable email notification delivery scaffold",
    )
    enable_imports: bool = Field(default=False, description="Enable data import pipeline")
    enable_enterprise: bool = Field(default=False, description="Enable enterprise-tier features")
    enable_billing: bool = Field(
        default=False,
        description="Enable Stripe billing scaffold",
    )
    enable_client_portal: bool = Field(
        default=False,
        description="Enable client-facing portal",
    )


_FLAG_FIELD_MAP: dict[FeatureFlag, str] = {
    FeatureFlag.ENABLE_AI: "enable_ai",
    FeatureFlag.ENABLE_LLM: "enable_llm",
    FeatureFlag.ENABLE_EMAIL_DELIVERY: "enable_email_delivery",
    FeatureFlag.ENABLE_IMPORTS: "enable_imports",
    FeatureFlag.ENABLE_ENTERPRISE: "enable_enterprise",
    FeatureFlag.ENABLE_BILLING: "enable_billing",
    FeatureFlag.ENABLE_CLIENT_PORTAL: "enable_client_portal",
}


@lru_cache
def get_feature_flags() -> FeatureFlags:
    return FeatureFlags()


def is_feature_enabled(flag: FeatureFlag) -> bool:
    flags = get_feature_flags()
    return bool(getattr(flags, _FLAG_FIELD_MAP[flag]))


def feature_flags_as_dict() -> dict[str, bool]:
    return {flag.value: is_feature_enabled(flag) for flag in FeatureFlag}
