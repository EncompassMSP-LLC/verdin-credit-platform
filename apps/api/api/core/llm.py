"""LLM policy gate API helpers."""

from verdin_llm_gateway import (
    LlmFeatureDisabledError,
    LlmGateStatus,
    LlmGatewaySettings,
    LlmPiiPolicyError,
    LlmProviderNotConfiguredError,
    evaluate_llm_gate,
    get_llm_settings,
    require_llm_ready,
)

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def is_llm_feature_enabled() -> bool:
    return is_feature_enabled(FeatureFlag.ENABLE_LLM)


def get_llm_gate_status(settings: LlmGatewaySettings | None = None) -> LlmGateStatus:
    return evaluate_llm_gate(
        feature_enabled=is_llm_feature_enabled(),
        settings=settings,
    )


def require_llm_gateway(*, requires_pii_export: bool = False) -> LlmGateStatus:
    return require_llm_ready(
        feature_enabled=is_llm_feature_enabled(),
        settings=get_llm_settings(),
        requires_pii_export=requires_pii_export,
    )


__all__ = [
    "LlmFeatureDisabledError",
    "LlmGateStatus",
    "LlmGatewaySettings",
    "LlmPiiPolicyError",
    "LlmProviderNotConfiguredError",
    "get_llm_gate_status",
    "is_llm_feature_enabled",
    "require_llm_gateway",
]
