"""Pydantic schemas for SAML federation metadata upload scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.saml_federation_metadata import SamlFederationMetadataStatus
from api.modules.enterprise.federation_metadata_models import (
    SamlFederationMetadataUpload,
    SamlMetadataValidationStatus,
)


class SamlFederationMetadataStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    federation_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls,
        status: SamlFederationMetadataStatus,
    ) -> "SamlFederationMetadataStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            federation_ready=status.federation_ready,
            blockers=list(status.blockers),
        )


class SamlFederationMetadataUploadRequest(BaseSchema):
    metadata_xml: str = Field(min_length=1)
    provider_key: str | None = Field(default=None, max_length=64)


class SamlFederationMetadataUploadResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    provider_key: str | None
    entity_id: str | None
    validation_status: SamlMetadataValidationStatus
    validation_message: str | None
    uploaded_by_user_id: uuid.UUID | None
    uploaded_at: datetime | None

    @classmethod
    def from_model(
        cls,
        upload: SamlFederationMetadataUpload,
    ) -> "SamlFederationMetadataUploadResponse":
        return cls(
            id=upload.id,
            organization_id=upload.organization_id,
            provider_key=upload.provider_key,
            entity_id=upload.entity_id,
            validation_status=upload.validation_status,
            validation_message=upload.validation_message,
            uploaded_by_user_id=upload.uploaded_by_user_id,
            uploaded_at=upload.uploaded_at,
        )


class SamlFederationMetadataUploadListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SamlFederationMetadataUploadResultResponse(BaseSchema):
    uploaded_at: datetime
    upload: SamlFederationMetadataUploadResponse
