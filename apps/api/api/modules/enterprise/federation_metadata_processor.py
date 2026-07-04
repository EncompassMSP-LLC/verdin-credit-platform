"""SAML federation metadata upload processor scaffold."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.saml_federation_metadata import validate_saml_metadata_xml
from api.modules.enterprise.federation_metadata_models import (
    SamlFederationMetadataUpload,
    SamlMetadataValidationStatus,
)
from api.modules.enterprise.federation_metadata_repository import (
    SamlFederationMetadataUploadRepository,
)


@dataclass(frozen=True)
class SamlFederationMetadataUploadSummary:
    upload: SamlFederationMetadataUpload
    uploaded_at: datetime


async def upload_saml_federation_metadata(
    *,
    session: AsyncSession,
    organization_id: uuid.UUID,
    metadata_xml: str,
    provider_key: str | None,
    uploaded_by_user_id: uuid.UUID | None,
    upload_repo: SamlFederationMetadataUploadRepository | None = None,
) -> SamlFederationMetadataUploadSummary:
    uploads = upload_repo or SamlFederationMetadataUploadRepository(session)
    uploaded_at = uploads.utcnow()

    entity_id, error_message = validate_saml_metadata_xml(metadata_xml)
    if error_message is not None:
        upload = await uploads.create_upload(
            organization_id=organization_id,
            metadata_xml=metadata_xml,
            provider_key=provider_key,
            entity_id=None,
            validation_status=SamlMetadataValidationStatus.INVALID,
            validation_message=error_message,
            uploaded_by_user_id=uploaded_by_user_id,
            uploaded_at=uploaded_at,
        )
        return SamlFederationMetadataUploadSummary(upload=upload, uploaded_at=uploaded_at)

    upload = await uploads.create_upload(
        organization_id=organization_id,
        metadata_xml=metadata_xml,
        provider_key=provider_key,
        entity_id=entity_id,
        validation_status=SamlMetadataValidationStatus.VALID,
        validation_message=None,
        uploaded_by_user_id=uploaded_by_user_id,
        uploaded_at=uploaded_at,
    )
    return SamlFederationMetadataUploadSummary(upload=upload, uploaded_at=uploaded_at)
