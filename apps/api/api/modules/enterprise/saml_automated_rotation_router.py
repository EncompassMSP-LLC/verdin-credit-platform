"""Admin-gated SAML automated rotation endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.saml_automated_rotation_dependencies import (
    require_saml_automated_rotation_enabled,
)
from api.modules.enterprise.saml_automated_rotation_schemas import (
    SamlAutomatedRotationRunListParams,
    SamlAutomatedRotationRunResponse,
    SamlAutomatedRotationRunResultResponse,
    SamlAutomatedRotationStatusResponse,
    SamlAutomatedRotationSubmitRequest,
)
from api.modules.enterprise.saml_automated_rotation_service import SamlAutomatedRotationService

saml_automated_rotation_router = APIRouter(
    prefix="/saml-automated-rotation", tags=["SAML Automated Rotation"]
)


def get_saml_automated_rotation_service(
    db: AsyncSession = Depends(get_db),
) -> SamlAutomatedRotationService:
    return SamlAutomatedRotationService.from_session(db)


@saml_automated_rotation_router.get("/status", response_model=SamlAutomatedRotationStatusResponse)
async def get_saml_automated_rotation_status_endpoint(
    _: None = Depends(require_saml_automated_rotation_enabled),
    service: SamlAutomatedRotationService = Depends(get_saml_automated_rotation_service),
) -> SamlAutomatedRotationStatusResponse:
    return service.get_status_response()


@saml_automated_rotation_router.get(
    "/runs",
    response_model=PaginatedResponse[SamlAutomatedRotationRunResponse],
)
async def list_saml_automated_rotation_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_saml_automated_rotation_enabled),
    current_user: User = Depends(get_current_user),
    service: SamlAutomatedRotationService = Depends(get_saml_automated_rotation_service),
) -> PaginatedResponse[SamlAutomatedRotationRunResponse]:
    params = SamlAutomatedRotationRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@saml_automated_rotation_router.post(
    "/rotation-runs/{saml_certificate_rotation_run_id}/start",
    response_model=SamlAutomatedRotationRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_saml_automated_rotation_run_endpoint(
    saml_certificate_rotation_run_id: uuid.UUID,
    body: SamlAutomatedRotationSubmitRequest,
    _: None = Depends(require_saml_automated_rotation_enabled),
    current_user: User = Depends(get_current_user),
    service: SamlAutomatedRotationService = Depends(get_saml_automated_rotation_service),
) -> SamlAutomatedRotationRunResultResponse:
    return await service.submit_from_rotation_run(
        current_user, saml_certificate_rotation_run_id, body
    )


@saml_automated_rotation_router.post(
    "/runs/{run_id}/approve",
    response_model=SamlAutomatedRotationRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_saml_automated_rotation_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_saml_automated_rotation_enabled),
    current_user: User = Depends(get_current_user),
    service: SamlAutomatedRotationService = Depends(get_saml_automated_rotation_service),
) -> SamlAutomatedRotationRunResultResponse:
    return await service.approve_run(current_user, run_id)
