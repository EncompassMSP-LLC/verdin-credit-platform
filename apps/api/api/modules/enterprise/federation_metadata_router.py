"""SAML federation metadata upload scaffold endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.dependencies import require_saml_federation_metadata_enabled
from api.modules.enterprise.federation_metadata_schemas import (
    SamlFederationMetadataStatusResponse,
    SamlFederationMetadataUploadListParams,
    SamlFederationMetadataUploadRequest,
    SamlFederationMetadataUploadResponse,
    SamlFederationMetadataUploadResultResponse,
)
from api.modules.enterprise.federation_metadata_service import SamlFederationMetadataService

saml_metadata_router = APIRouter(prefix="/saml-metadata", tags=["SAML Federation Metadata"])


def get_saml_federation_metadata_service(
    db: AsyncSession = Depends(get_db),
) -> SamlFederationMetadataService:
    return SamlFederationMetadataService.from_session(db)


@saml_metadata_router.get("/status", response_model=SamlFederationMetadataStatusResponse)
async def get_saml_federation_metadata_status_endpoint(
    _: None = Depends(require_saml_federation_metadata_enabled),
    service: SamlFederationMetadataService = Depends(get_saml_federation_metadata_service),
) -> SamlFederationMetadataStatusResponse:
    return service.get_status_response()


@saml_metadata_router.get(
    "/uploads",
    response_model=PaginatedResponse[SamlFederationMetadataUploadResponse],
)
async def list_saml_federation_metadata_uploads(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_saml_federation_metadata_enabled),
    current_user: User = Depends(get_current_user),
    service: SamlFederationMetadataService = Depends(get_saml_federation_metadata_service),
) -> PaginatedResponse[SamlFederationMetadataUploadResponse]:
    params = SamlFederationMetadataUploadListParams(page=page, page_size=page_size)
    return await service.list_uploads(current_user, params)


@saml_metadata_router.post(
    "/upload",
    response_model=SamlFederationMetadataUploadResultResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_saml_federation_metadata_endpoint(
    body: SamlFederationMetadataUploadRequest,
    _: None = Depends(require_saml_federation_metadata_enabled),
    current_user: User = Depends(get_current_user),
    service: SamlFederationMetadataService = Depends(get_saml_federation_metadata_service),
) -> SamlFederationMetadataUploadResultResponse:
    return await service.upload_metadata(current_user, body)
