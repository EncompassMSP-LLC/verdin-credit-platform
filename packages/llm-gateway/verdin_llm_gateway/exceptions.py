"""LLM gateway exceptions."""


class LlmGatewayError(Exception):
    """Base error for LLM gateway failures."""


class LlmFeatureDisabledError(LlmGatewayError):
    """Raised when ENABLE_LLM is false."""


class LlmProviderNotConfiguredError(LlmGatewayError):
    """Raised when provider credentials or model are missing."""


class LlmPiiPolicyError(LlmGatewayError):
    """Raised when content would export PII without explicit org opt-in."""
