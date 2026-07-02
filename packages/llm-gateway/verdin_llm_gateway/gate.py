"""LLM readiness evaluation and enforcement."""

from dataclasses import dataclass

from verdin_llm_gateway.config import LlmGatewaySettings, get_llm_settings
from verdin_llm_gateway.exceptions import (
    LlmFeatureDisabledError,
    LlmPiiPolicyError,
    LlmProviderNotConfiguredError,
)


@dataclass(frozen=True, slots=True)
class LlmGateStatus:
    feature_enabled: bool
    provider_configured: bool
    pii_export_allowed: bool
    provider: str
    model: str | None
    ready: bool
    blockers: tuple[str, ...]


def evaluate_llm_gate(
    *,
    feature_enabled: bool,
    settings: LlmGatewaySettings | None = None,
) -> LlmGateStatus:
    config = settings or get_llm_settings()
    blockers: list[str] = []

    if not feature_enabled:
        blockers.append("ENABLE_LLM is false")
    if not config.is_provider_configured:
        blockers.append("LLM provider credentials or model are not configured")

    ready = feature_enabled and config.is_provider_configured
    return LlmGateStatus(
        feature_enabled=feature_enabled,
        provider_configured=config.is_provider_configured,
        pii_export_allowed=config.llm_allow_external_pii_export,
        provider=config.llm_provider.value,
        model=config.llm_model,
        ready=ready,
        blockers=tuple(blockers),
    )


def require_llm_ready(
    *,
    feature_enabled: bool,
    settings: LlmGatewaySettings | None = None,
    requires_pii_export: bool = False,
) -> LlmGateStatus:
    status = evaluate_llm_gate(feature_enabled=feature_enabled, settings=settings)
    if not status.feature_enabled:
        raise LlmFeatureDisabledError("LLM features are disabled (ENABLE_LLM=false)")
    if not status.provider_configured:
        raise LlmProviderNotConfiguredError(
            "LLM provider is not configured. Set LLM_PROVIDER, LLM_API_KEY, and LLM_MODEL."
        )
    if requires_pii_export and not status.pii_export_allowed:
        raise LlmPiiPolicyError(
            "External PII export is blocked. Set LLM_ALLOW_EXTERNAL_PII_EXPORT=true to opt in."
        )
    return status
