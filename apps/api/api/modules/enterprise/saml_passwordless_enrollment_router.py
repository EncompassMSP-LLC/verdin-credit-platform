"""Admin-gated SAML passwordless enrollment endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.saml_passwordless_enrollment_dependencies import (
    require_saml_passwordless_enrollment_enabled,
)
from api.modules.enterprise.saml_passwordless_enrollment_schemas import (
    SamlPasswordlessEnrollmentRunListParams,
    SamlPasswordlessEnrollmentRunResponse,
    SamlPasswordlessEnrollmentRunResultResponse,
    SamlPasswordlessEnrollmentStatusResponse,
    SamlPasswordlessEnrollmentSubmitRequest,
)
from api.modules.enterprise.saml_passwordless_enrollment_service import (
    SamlPasswordlessEnrollmentService,
)

saml_passwordless_enrollment_router = APIRouter(
    prefix="/saml-passwordless-enrollment",
    tags=["SAML Passwordless Enrollment"],
)


def get_saml_passwordless_enrollment_service(
    db: AsyncSession = Depends(get_db),
) -> SamlPasswordlessEnrollmentService:
    return SamlPasswordlessEnrollmentService.from_session(db)


@saml_passwordless_enrollment_router.get(
    "/status", response_model=SamlPasswordlessEnrollmentStatusResponse
)
async def get_saml_passwordless_enrollment_status_endpoint(
    _: None = Depends(require_saml_passwordless_enrollment_enabled),
    service: SamlPasswordlessEnrollmentService = Depends(get_saml_passwordless_enrollment_service),
) -> SamlPasswordlessEnrollmentStatusResponse:
    return service.get_status_response()


@saml_passwordless_enrollment_router.get(
    "/runs",
    response_model=PaginatedResponse[SamlPasswordlessEnrollmentRunResponse],
)
async def list_saml_passwordless_enrollment_runs(
    page: int = 1,
    page_size: int = 20,
    _: None = Depends(require_saml_passwordless_enrollment_enabled),
    current_user: User = Depends(get_current_user),
    service: SamlPasswordlessEnrollmentService = Depends(get_saml_passwordless_enrollment_service),
) -> PaginatedResponse[SamlPasswordlessEnrollmentRunResponse]:
    params = SamlPasswordlessEnrollmentRunListParams(page=page, page_size=page_size)
    return await service.list_runs(current_user, params)


@saml_passwordless_enrollment_router.post(
    "/automated-rotation-runs/{saml_automated_rotation_run_id}/enroll",
    response_model=SamlPasswordlessEnrollmentRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_saml_passwordless_enrollment_run_endpoint(
    saml_automated_rotation_run_id: uuid.UUID,
    body: SamlPasswordlessEnrollmentSubmitRequest,
    _: None = Depends(require_saml_passwordless_enrollment_enabled),
    current_user: User = Depends(get_current_user),
    service: SamlPasswordlessEnrollmentService = Depends(get_saml_passwordless_enrollment_service),
) -> SamlPasswordlessEnrollmentRunResultResponse:
    return await service.submit_from_automated_rotation_run(
        current_user, saml_automated_rotation_run_id, body
    )


@saml_passwordless_enrollment_router.post(
    "/runs/{run_id}/approve",
    response_model=SamlPasswordlessEnrollmentRunResultResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_saml_passwordless_enrollment_run_endpoint(
    run_id: uuid.UUID,
    _: None = Depends(require_saml_passwordless_enrollment_enabled),
    current_user: User = Depends(get_current_user),
    service: SamlPasswordlessEnrollmentService = Depends(get_saml_passwordless_enrollment_service),
) -> SamlPasswordlessEnrollmentRunResultResponse:
    return await service.approve_run(current_user, run_id)
