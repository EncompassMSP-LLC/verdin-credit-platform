"""LLM provider configuration."""

from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LlmProvider(StrEnum):
    NONE = "none"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"


class LlmGatewaySettings(BaseSettings):
    """Provider settings read from ``LLM_*`` environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    llm_provider: LlmProvider = Field(default=LlmProvider.NONE, description="Active LLM vendor")
    llm_api_key: str | None = Field(default=None, description="Provider API key")
    llm_model: str | None = Field(default=None, description="Default model identifier")
    llm_base_url: str | None = Field(default=None, description="Optional provider base URL")
    llm_timeout_seconds: int = Field(default=30, ge=5, le=300)
    llm_allow_external_pii_export: bool = Field(
        default=False,
        description="Explicit opt-in to send PII to external LLM providers",
    )

    @property
    def is_provider_configured(self) -> bool:
        if self.llm_provider is LlmProvider.NONE:
            return False
        if not self.llm_api_key or not self.llm_model:
            return False
        if self.llm_provider is LlmProvider.AZURE_OPENAI and not self.llm_base_url:
            return False
        return True


@lru_cache
def get_llm_settings() -> LlmGatewaySettings:
    return LlmGatewaySettings()
