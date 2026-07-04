"""Pydantic schemas for IdP federation scaffold."""

import uuid

from pydantic import Field, field_validator

from api.core.idp_federation import IdpFederationStatus
from api.core.responses import BaseSchema
from api.modules.enterprise.federation_models import (
    IdpFederationProvider,
    IdpFederationProviderType,
)


class IdpFederationStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    scim_provisioning_enabled: bool
    provider_count: int
    blockers: list[str]

    @classmethod
    def from_status(
        cls,
        status: IdpFederationStatus,
        *,
        provider_count: int,
    ) -> "IdpFederationStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            scim_provisioning_enabled=status.scim_provisioning_enabled,
            provider_count=provider_count,
            blockers=list(status.blockers),
        )


class IdpFederationProviderRegisterRequest(BaseSchema):
    provider_key: str = Field(min_length=1, max_length=64)
    provider_type: IdpFederationProviderType
    display_name: str = Field(min_length=1, max_length=120)
    issuer_url: str | None = Field(default=None, max_length=500)
    is_primary: bool = False
    enabled: bool = True

    @field_validator("provider_key")
    @classmethod
    def normalize_provider_key(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("provider_key must not be empty")
        return normalized


class IdpFederationProviderResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    provider_key: str
    provider_type: IdpFederationProviderType
    display_name: str
    issuer_url: str | None
    is_primary: bool
    enabled: bool
    registered_by_user_id: uuid.UUID | None

    @classmethod
    def from_model(cls, provider: IdpFederationProvider) -> "IdpFederationProviderResponse":
        return cls(
            id=provider.id,
            organization_id=provider.organization_id,
            provider_key=provider.provider_key,
            provider_type=provider.provider_type,
            display_name=provider.display_name,
            issuer_url=provider.issuer_url,
            is_primary=provider.is_primary,
            enabled=provider.enabled,
            registered_by_user_id=provider.registered_by_user_id,
        )


class IdpFederationProviderListResponse(BaseSchema):
    total_results: int
    providers: list[IdpFederationProviderResponse]
