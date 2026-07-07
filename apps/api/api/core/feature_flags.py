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
    ENABLE_BILLING_USAGE_METERING = "ENABLE_BILLING_USAGE_METERING"
    ENABLE_SCIM_PROVISIONING = "ENABLE_SCIM_PROVISIONING"
    ENABLE_PREDICTIVE_ANALYTICS = "ENABLE_PREDICTIVE_ANALYTICS"
    ENABLE_API_DEVELOPER_PORTAL = "ENABLE_API_DEVELOPER_PORTAL"
    ENABLE_PUBLIC_OAUTH_DEVELOPER_PORTAL = "ENABLE_PUBLIC_OAUTH_DEVELOPER_PORTAL"
    ENABLE_CROSS_ORG_BENCHMARK_ANALYTICS = "ENABLE_CROSS_ORG_BENCHMARK_ANALYTICS"
    ENABLE_BATCH_LLM_SUMMARIES = "ENABLE_BATCH_LLM_SUMMARIES"
    ENABLE_BILLING_INVOICING = "ENABLE_BILLING_INVOICING"
    ENABLE_BILLING_INVOICE_COLLECTION = "ENABLE_BILLING_INVOICE_COLLECTION"
    ENABLE_IDP_FEDERATION = "ENABLE_IDP_FEDERATION"
    ENABLE_SAML_FEDERATION_METADATA = "ENABLE_SAML_FEDERATION_METADATA"
    ENABLE_HRIS_BIDIRECTIONAL_SYNC = "ENABLE_HRIS_BIDIRECTIONAL_SYNC"
    ENABLE_SMS_MARKETING_CAMPAIGNS = "ENABLE_SMS_MARKETING_CAMPAIGNS"
    ENABLE_SMS_MARKETING_DELIVERY = "ENABLE_SMS_MARKETING_DELIVERY"
    ENABLE_SMS_DELIVERABILITY_DASHBOARD = "ENABLE_SMS_DELIVERABILITY_DASHBOARD"
    ENABLE_LLM_DISPUTE_DRAFT_AUGMENT = "ENABLE_LLM_DISPUTE_DRAFT_AUGMENT"
    ENABLE_AGENT_OBSERVABILITY = "ENABLE_AGENT_OBSERVABILITY"
    ENABLE_AGENT_EXECUTION = "ENABLE_AGENT_EXECUTION"
    ENABLE_DISPUTE_FILING_PREP = "ENABLE_DISPUTE_FILING_PREP"
    ENABLE_DISPUTE_BUREAU_SUBMISSION = "ENABLE_DISPUTE_BUREAU_SUBMISSION"
    ENABLE_AGENT_EXTERNAL_TOOL_CALLING = "ENABLE_AGENT_EXTERNAL_TOOL_CALLING"
    ENABLE_SAML_CERTIFICATE_ROTATION = "ENABLE_SAML_CERTIFICATE_ROTATION"
    ENABLE_SAML_AUTOMATED_ROTATION = "ENABLE_SAML_AUTOMATED_ROTATION"
    ENABLE_SAML_PASSWORDLESS_ENROLLMENT = "ENABLE_SAML_PASSWORDLESS_ENROLLMENT"
    ENABLE_HRIS_PASSWORDLESS_UI = "ENABLE_HRIS_PASSWORDLESS_UI"
    ENABLE_MOBILE_PASSKEY_READINESS = "ENABLE_MOBILE_PASSKEY_READINESS"
    ENABLE_MULTI_IDP_BULK_PROVISIONING = "ENABLE_MULTI_IDP_BULK_PROVISIONING"
    ENABLE_STRIPE_INVOICE_PDF = "ENABLE_STRIPE_INVOICE_PDF"
    ENABLE_AGENT_SUPERVISED_LOOPS = "ENABLE_AGENT_SUPERVISED_LOOPS"
    ENABLE_AGENT_UNSUPERVISED_LOOPS = "ENABLE_AGENT_UNSUPERVISED_LOOPS"
    ENABLE_AGENT_ARBITRARY_EXECUTION = "ENABLE_AGENT_ARBITRARY_EXECUTION"
    ENABLE_BUREAU_LIVE_API = "ENABLE_BUREAU_LIVE_API"
    ENABLE_AUTONOMOUS_BUREAU_FILING = "ENABLE_AUTONOMOUS_BUREAU_FILING"
    ENABLE_BUREAU_REFILING = "ENABLE_BUREAU_REFILING"
    ENABLE_BUREAU_UNSUPERVISED_REFILING = "ENABLE_BUREAU_UNSUPERVISED_REFILING"
    ENABLE_STRIPE_TAX_CALCULATION = "ENABLE_STRIPE_TAX_CALCULATION"
    ENABLE_STRIPE_LIVE_TAX_API = "ENABLE_STRIPE_LIVE_TAX_API"
    ENABLE_STRIPE_CHARGE_RETRY = "ENABLE_STRIPE_CHARGE_RETRY"
    ENABLE_STRIPE_LIVE_CHARGE_RETRY_EXECUTION = "ENABLE_STRIPE_LIVE_CHARGE_RETRY_EXECUTION"
    ENABLE_HRIS_LIFECYCLE_SYNC = "ENABLE_HRIS_LIFECYCLE_SYNC"


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
    enable_billing_usage_metering: bool = Field(
        default=False,
        description="Enable org-scoped billing usage event recording and summary reads",
    )
    enable_scim_provisioning: bool = Field(
        default=False,
        description="Enable SCIM 2.0 user and group provision scaffold",
    )
    enable_predictive_analytics: bool = Field(
        default=False,
        description="Enable org-scoped predictive outcome aggregates and refresh scaffold",
    )
    enable_api_developer_portal: bool = Field(
        default=False,
        description="Enable internal API developer portal and key rotation workflow",
    )
    enable_public_oauth_developer_portal: bool = Field(
        default=False,
        description="Enable public OAuth developer portal app registration audit scaffold",
    )
    enable_cross_org_benchmark_analytics: bool = Field(
        default=False,
        description="Enable governance-gated cross-org benchmark analytics scaffold",
    )
    enable_batch_llm_summaries: bool = Field(
        default=False,
        description="Enable batch document LLM summarization worker job scaffold",
    )
    enable_billing_invoicing: bool = Field(
        default=False,
        description="Enable org-scoped billing invoicing and dunning run scaffold",
    )
    enable_billing_invoice_collection: bool = Field(
        default=False,
        description="Enable org-scoped billing invoice PDF and payment collection scaffold",
    )
    enable_idp_federation: bool = Field(
        default=False,
        description="Enable multi-IdP federation provider registry scaffold",
    )
    enable_saml_federation_metadata: bool = Field(
        default=False,
        description="Enable SAML metadata upload and validation scaffold",
    )
    enable_hris_bidirectional_sync: bool = Field(
        default=False,
        description="Enable HRIS bidirectional sync run audit scaffold",
    )
    enable_sms_marketing_campaigns: bool = Field(
        default=False,
        description="Enable marketing SMS campaign enqueue scaffold",
    )
    enable_sms_marketing_delivery: bool = Field(
        default=False,
        description="Enable marketing SMS campaign delivery worker",
    )
    enable_sms_deliverability_dashboard: bool = Field(
        default=False,
        description="Enable SMS marketing deliverability metrics read model",
    )
    enable_llm_dispute_draft_augment: bool = Field(
        default=False,
        description="Enable ADR-012-gated LLM dispute draft augment scaffold",
    )
    enable_agent_observability: bool = Field(
        default=False,
        description="Enable agent run audit and observability read scaffold",
    )
    enable_agent_execution: bool = Field(
        default=False,
        description="Enable human-gated agent execution step scaffold",
    )
    enable_dispute_filing_prep: bool = Field(
        default=False,
        description="Enable compliance-gated dispute filing prep audit scaffold",
    )
    enable_dispute_bureau_submission: bool = Field(
        default=False,
        description="Enable admin-gated dispute bureau submission audit scaffold",
    )
    enable_agent_external_tool_calling: bool = Field(
        default=False,
        description="Enable human-gated agent external tool invocation audit scaffold",
    )
    enable_saml_certificate_rotation: bool = Field(
        default=False,
        description="Enable admin-gated SAML certificate rotation audit scaffold",
    )
    enable_saml_automated_rotation: bool = Field(
        default=False,
        description="Enable admin-gated SAML automated rotation audit scaffold",
    )
    enable_saml_passwordless_enrollment: bool = Field(
        default=False,
        description="Enable admin-gated SAML passwordless enrollment audit scaffold",
    )
    enable_hris_passwordless_ui: bool = Field(
        default=False,
        description="Enable admin-gated HRIS passwordless UI audit scaffold",
    )
    enable_mobile_passkey_readiness: bool = Field(
        default=False,
        description="Enable admin-gated mobile passkey readiness audit scaffold",
    )
    enable_multi_idp_bulk_provisioning: bool = Field(
        default=False,
        description="Enable admin-gated multi-IdP bulk provisioning audit scaffold",
    )
    enable_stripe_invoice_pdf: bool = Field(
        default=False,
        description="Enable admin-gated Stripe invoice PDF generation audit scaffold",
    )
    enable_agent_supervised_loops: bool = Field(
        default=False,
        description="Enable human-gated agent supervised loop audit scaffold",
    )
    enable_agent_unsupervised_loops: bool = Field(
        default=False,
        description="Enable admin-gated agent unsupervised loop audit scaffold",
    )
    enable_agent_arbitrary_execution: bool = Field(
        default=False,
        description="Enable admin-gated agent arbitrary execution audit scaffold",
    )
    enable_bureau_live_api: bool = Field(
        default=False,
        description="Enable operator-gated bureau live API invocation audit scaffold",
    )
    enable_autonomous_bureau_filing: bool = Field(
        default=False,
        description="Enable admin-gated autonomous bureau filing audit scaffold",
    )
    enable_bureau_refiling: bool = Field(
        default=False,
        description="Enable operator-gated bureau re-filing audit scaffold",
    )
    enable_bureau_unsupervised_refiling: bool = Field(
        default=False,
        description="Enable operator-gated bureau unsupervised re-filing audit scaffold",
    )
    enable_stripe_tax_calculation: bool = Field(
        default=False,
        description="Enable admin-gated Stripe tax calculation audit scaffold",
    )
    enable_stripe_live_tax_api: bool = Field(
        default=False,
        description="Enable admin-gated Stripe live Tax API invocation audit scaffold",
    )
    enable_stripe_charge_retry: bool = Field(
        default=False,
        description="Enable admin-gated Stripe charge retry audit scaffold",
    )
    enable_stripe_live_charge_retry_execution: bool = Field(
        default=False,
        description="Enable admin-gated Stripe live charge retry execution audit scaffold",
    )
    enable_hris_lifecycle_sync: bool = Field(
        default=False,
        description="Enable admin-gated HRIS lifecycle sync audit scaffold",
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
    FeatureFlag.ENABLE_BILLING_USAGE_METERING: "enable_billing_usage_metering",
    FeatureFlag.ENABLE_SCIM_PROVISIONING: "enable_scim_provisioning",
    FeatureFlag.ENABLE_PREDICTIVE_ANALYTICS: "enable_predictive_analytics",
    FeatureFlag.ENABLE_API_DEVELOPER_PORTAL: "enable_api_developer_portal",
    FeatureFlag.ENABLE_PUBLIC_OAUTH_DEVELOPER_PORTAL: "enable_public_oauth_developer_portal",
    FeatureFlag.ENABLE_CROSS_ORG_BENCHMARK_ANALYTICS: "enable_cross_org_benchmark_analytics",
    FeatureFlag.ENABLE_BATCH_LLM_SUMMARIES: "enable_batch_llm_summaries",
    FeatureFlag.ENABLE_BILLING_INVOICING: "enable_billing_invoicing",
    FeatureFlag.ENABLE_BILLING_INVOICE_COLLECTION: "enable_billing_invoice_collection",
    FeatureFlag.ENABLE_IDP_FEDERATION: "enable_idp_federation",
    FeatureFlag.ENABLE_SAML_FEDERATION_METADATA: "enable_saml_federation_metadata",
    FeatureFlag.ENABLE_HRIS_BIDIRECTIONAL_SYNC: "enable_hris_bidirectional_sync",
    FeatureFlag.ENABLE_SMS_MARKETING_CAMPAIGNS: "enable_sms_marketing_campaigns",
    FeatureFlag.ENABLE_SMS_MARKETING_DELIVERY: "enable_sms_marketing_delivery",
    FeatureFlag.ENABLE_SMS_DELIVERABILITY_DASHBOARD: "enable_sms_deliverability_dashboard",
    FeatureFlag.ENABLE_LLM_DISPUTE_DRAFT_AUGMENT: "enable_llm_dispute_draft_augment",
    FeatureFlag.ENABLE_AGENT_OBSERVABILITY: "enable_agent_observability",
    FeatureFlag.ENABLE_AGENT_EXECUTION: "enable_agent_execution",
    FeatureFlag.ENABLE_DISPUTE_FILING_PREP: "enable_dispute_filing_prep",
    FeatureFlag.ENABLE_DISPUTE_BUREAU_SUBMISSION: "enable_dispute_bureau_submission",
    FeatureFlag.ENABLE_AGENT_EXTERNAL_TOOL_CALLING: "enable_agent_external_tool_calling",
    FeatureFlag.ENABLE_SAML_CERTIFICATE_ROTATION: "enable_saml_certificate_rotation",
    FeatureFlag.ENABLE_SAML_AUTOMATED_ROTATION: "enable_saml_automated_rotation",
    FeatureFlag.ENABLE_SAML_PASSWORDLESS_ENROLLMENT: "enable_saml_passwordless_enrollment",
    FeatureFlag.ENABLE_HRIS_PASSWORDLESS_UI: "enable_hris_passwordless_ui",
    FeatureFlag.ENABLE_MOBILE_PASSKEY_READINESS: "enable_mobile_passkey_readiness",
    FeatureFlag.ENABLE_MULTI_IDP_BULK_PROVISIONING: "enable_multi_idp_bulk_provisioning",
    FeatureFlag.ENABLE_STRIPE_INVOICE_PDF: "enable_stripe_invoice_pdf",
    FeatureFlag.ENABLE_AGENT_SUPERVISED_LOOPS: "enable_agent_supervised_loops",
    FeatureFlag.ENABLE_AGENT_UNSUPERVISED_LOOPS: "enable_agent_unsupervised_loops",
    FeatureFlag.ENABLE_AGENT_ARBITRARY_EXECUTION: "enable_agent_arbitrary_execution",
    FeatureFlag.ENABLE_BUREAU_LIVE_API: "enable_bureau_live_api",
    FeatureFlag.ENABLE_AUTONOMOUS_BUREAU_FILING: "enable_autonomous_bureau_filing",
    FeatureFlag.ENABLE_BUREAU_REFILING: "enable_bureau_refiling",
    FeatureFlag.ENABLE_BUREAU_UNSUPERVISED_REFILING: "enable_bureau_unsupervised_refiling",
    FeatureFlag.ENABLE_STRIPE_TAX_CALCULATION: "enable_stripe_tax_calculation",
    FeatureFlag.ENABLE_STRIPE_LIVE_TAX_API: "enable_stripe_live_tax_api",
    FeatureFlag.ENABLE_STRIPE_CHARGE_RETRY: "enable_stripe_charge_retry",
    FeatureFlag.ENABLE_STRIPE_LIVE_CHARGE_RETRY_EXECUTION: (
        "enable_stripe_live_charge_retry_execution"
    ),
    FeatureFlag.ENABLE_HRIS_LIFECYCLE_SYNC: "enable_hris_lifecycle_sync",
}


@lru_cache
def get_feature_flags() -> FeatureFlags:
    return FeatureFlags()


def is_feature_enabled(flag: FeatureFlag) -> bool:
    flags = get_feature_flags()
    return bool(getattr(flags, _FLAG_FIELD_MAP[flag]))


def feature_flags_as_dict() -> dict[str, bool]:
    return {flag.value: is_feature_enabled(flag) for flag in FeatureFlag}
