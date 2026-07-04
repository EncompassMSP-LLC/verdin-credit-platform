"""SAML federation metadata upload service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.core.saml_federation_metadata import get_saml_federation_metadata_status
from api.modules.auth.models import User
from api.modules.enterprise.federation_metadata_models import SamlMetadataValidationStatus
from api.modules.enterprise.federation_metadata_processor import upload_saml_federation_metadata
from api.modules.enterprise.federation_metadata_repository import (
    SamlFederationMetadataUploadListFilters,
    SamlFederationMetadataUploadRepository,
)
from api.modules.enterprise.federation_metadata_schemas import (
    SamlFederationMetadataStatusResponse,
    SamlFederationMetadataUploadListParams,
    SamlFederationMetadataUploadRequest,
    SamlFederationMetadataUploadResponse,
    SamlFederationMetadataUploadResultResponse,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class SamlFederationMetadataService:
    def __init__(
        self,
        upload_repo: SamlFederationMetadataUploadRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._uploads = upload_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> SamlFederationMetadataService:
        return cls(SamlFederationMetadataUploadRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view SAML metadata uploads",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to upload SAML metadata",
            )

    def get_status_response(self) -> SamlFederationMetadataStatusResponse:
        return SamlFederationMetadataStatusResponse.from_status(
            get_saml_federation_metadata_status()
        )

    async def list_uploads(
        self,
        user: User,
        params: SamlFederationMetadataUploadListParams,
    ) -> PaginatedResponse[SamlFederationMetadataUploadResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )
        skip = (params.page - 1) * params.page_size
        uploads, total = await self._uploads.list_uploads(
            organization_id,
            SamlFederationMetadataUploadListFilters(skip=skip, limit=params.page_size),
        )
        items = [SamlFederationMetadataUploadResponse.from_model(item) for item in uploads]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def upload_metadata(
        self,
        user: User,
        body: SamlFederationMetadataUploadRequest,
    ) -> SamlFederationMetadataUploadResultResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        metadata_status = get_saml_federation_metadata_status()
        if not metadata_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "SAML federation metadata upload is not ready",
                    "blockers": list(metadata_status.blockers),
                },
            )
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        summary = await upload_saml_federation_metadata(
            session=self._session,
            organization_id=organization_id,
            metadata_xml=body.metadata_xml,
            provider_key=body.provider_key,
            uploaded_by_user_id=user.id,
        )
        if summary.upload.validation_status == SamlMetadataValidationStatus.INVALID:
            await self._session.commit()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=summary.upload.validation_message or "SAML metadata validation failed",
            )
        await self._session.commit()
        return SamlFederationMetadataUploadResultResponse(
            uploaded_at=summary.uploaded_at,
            upload=SamlFederationMetadataUploadResponse.from_model(summary.upload),
        )
