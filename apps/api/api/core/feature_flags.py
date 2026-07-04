"""Feature flags loaded from environment variables."""

from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FeatureFlag(StrEnum):
    ENABLE_AI = "ENABLE_AI"
    ENABLE_LLM = "ENABLE_LLM"
    ENABLE_EMAIL_DELIVERY = "ENABLE_EMAIL_DELIVERY"
    ENABLE_SMS_DELIVERY = "ENABLE_SMS_DELIVERY"
    ENABLE_IMPORTS = "ENABLE_IMPORTS"
    ENABLE_ENTERPRISE = "ENABLE_ENTERPRISE"
    ENABLE_BILLING = "ENABLE_BILLING"
    ENABLE_COMPLIANCE_ENFORCEMENT = "ENABLE_COMPLIANCE_ENFORCEMENT"
    ENABLE_CLIENT_PORTAL = "ENABLE_CLIENT_PORTAL"
    ENABLE_PORTAL_PUSH = "ENABLE_PORTAL_PUSH"
    ENABLE_MATERIALIZED_REPORTING = "ENABLE_MATERIALIZED_REPORTING"
    ENABLE_API_KEY_RATE_LIMIT = "ENABLE_API_KEY_RATE_LIMIT"


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
    enable_sms_delivery: bool = Field(
        default=False,
        description="Enable SMS notification delivery",
    )
    enable_imports: bool = Field(default=False, description="Enable data import pipeline")
    enable_enterprise: bool = Field(default=False, description="Enable enterprise-tier features")
    enable_billing: bool = Field(
        default=False,
        description="Enable Stripe billing scaffold",
    )
    enable_compliance_enforcement: bool = Field(
        default=False,
        description="Enable retention enforcement jobs",
    )
    enable_client_portal: bool = Field(
        default=False,
        description="Enable client-facing portal",
    )
    enable_portal_push: bool = Field(
        default=False,
        description="Enable portal push notification scaffold",
    )
    enable_materialized_reporting: bool = Field(
        default=False,
        description="Enable materialized reporting views for bureau and team metrics",
    )
    enable_api_key_rate_limit: bool = Field(
        default=False,
        description="Enable per-organization API key rate limiting on reporting operations",
    )


_FLAG_FIELD_MAP: dict[FeatureFlag, str] = {
    FeatureFlag.ENABLE_AI: "enable_ai",
    FeatureFlag.ENABLE_LLM: "enable_llm",
    FeatureFlag.ENABLE_EMAIL_DELIVERY: "enable_email_delivery",
    FeatureFlag.ENABLE_SMS_DELIVERY: "enable_sms_delivery",
    FeatureFlag.ENABLE_IMPORTS: "enable_imports",
    FeatureFlag.ENABLE_ENTERPRISE: "enable_enterprise",
    FeatureFlag.ENABLE_BILLING: "enable_billing",
    FeatureFlag.ENABLE_COMPLIANCE_ENFORCEMENT: "enable_compliance_enforcement",
    FeatureFlag.ENABLE_CLIENT_PORTAL: "enable_client_portal",
    FeatureFlag.ENABLE_PORTAL_PUSH: "enable_portal_push",
    FeatureFlag.ENABLE_MATERIALIZED_REPORTING: "enable_materialized_reporting",
    FeatureFlag.ENABLE_API_KEY_RATE_LIMIT: "enable_api_key_rate_limit",
}


@lru_cache
def get_feature_flags() -> FeatureFlags:
    return FeatureFlags()


def is_feature_enabled(flag: FeatureFlag) -> bool:
    flags = get_feature_flags()
    return bool(getattr(flags, _FLAG_FIELD_MAP[flag]))


def feature_flags_as_dict() -> dict[str, bool]:
    return {flag.value: is_feature_enabled(flag) for flag in FeatureFlag}
