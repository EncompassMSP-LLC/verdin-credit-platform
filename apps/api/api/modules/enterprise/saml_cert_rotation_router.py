"""Admin-gated SAML certificate rotation endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.dependencies import require_saml_certificate_rotation_enabled
from api.modules.enterprise.saml_cert_rotation_schemas import (
    SamlCertificateRotationRequest,
    SamlCertificateRotationRunListParams,
    SamlCertificateRotationRunResponse,
    SamlCertificateRotationRunResultResponse,
    SamlCertificateRotationStatusResponse,
)
from api.modules.enterprise.saml_cert_rotation_service import SamlCertificateRotationService

saml_cert_rotation_router = APIRouter(
    prefix="/saml-cert-rotation",
    tags=["SAML Certificate Rotation"],
)


def get_saml_certificate_rotation_service(
    db: AsyncSession = Depends(get_db),
) -> SamlCertificateRotationService:
    return SamlCertificateRotationService.from_session(db)


@saml_cert_rotation_router.get("/status", response_model=SamlCertificateRotationStatusResponse)
async def get_saml_certificate_rotation_status_endpoint(
    _: None = Depends(require_saml_certificate_rotation_enabled),
    service: SamlCertificateRotationService = Depends(get_saml_certificate_rotation_service),
) -> SamlCertificateRotationStatusResponse:
    return service.get_status_response()


@saml_cert_rotation_router.get(
    "/runs",
    response_model=PaginatedResponse[SamlCertificateRotationRunResponse],
)
async def list_saml_certificate_rotation_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_saml_certificate_rotation_enabled),
    current_user: User = Depends(get_current_user),
    service: SamlCertificateRotationService = Depends(get_saml_certificate_rotation_service),
) -> PaginatedResponse[SamlCertificateRotationRunResponse]:
    params = SamlCertificateRotationRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@saml_cert_rotation_router.post(
    "/metadata-uploads/{metadata_upload_id}/rotate",
    response_model=SamlCertificateRotationRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_saml_certificate_rotation_endpoint(
    metadata_upload_id: uuid.UUID,
    body: SamlCertificateRotationRequest,
    _: None = Depends(require_saml_certificate_rotation_enabled),
    current_user: User = Depends(get_current_user),
    service: SamlCertificateRotationService = Depends(get_saml_certificate_rotation_service),
) -> SamlCertificateRotationRunResultResponse:
    return await service.submit_from_metadata_upload(current_user, metadata_upload_id, body)


@saml_cert_rotation_router.post(
    "/runs/{run_id}/approve",
    response_model=SamlCertificateRotationRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_saml_certificate_rotation_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_saml_certificate_rotation_enabled),
    current_user: User = Depends(get_current_user),
    service: SamlCertificateRotationService = Depends(get_saml_certificate_rotation_service),
) -> SamlCertificateRotationRunResultResponse:
    return await service.approve_run(current_user, run_id)
