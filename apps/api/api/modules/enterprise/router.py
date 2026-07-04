"""Enterprise identity readiness and enrollment endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.enterprise import get_enterprise_identity_gate_status
from api.core.enterprise_identity import EnterpriseIdentityStatus
from api.core.responses import BaseSchema
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.enterprise.schemas import (
    SsoEnrollmentCompleteRequest,
    SsoEnrollmentCompleteResponse,
    SsoEnrollmentStartResponse,
    SsoEnrollmentStatusResponse,
    TotpEnrollmentConfirmRequest,
    TotpEnrollmentStartResponse,
    TotpEnrollmentStatusResponse,
)
from api.modules.enterprise.scim_router import scim_router
from api.modules.enterprise.service import EnterpriseEnrollmentService

router = APIRouter(prefix="/enterprise", tags=["Enterprise"])
router.include_router(scim_router)


class EnterpriseIdentityStatusResponse(BaseSchema):
    feature_enabled: bool
    sso_provider: str
    sso_ready: bool
    mfa_mode: str
    mfa_ready: bool
    ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: EnterpriseIdentityStatus) -> "EnterpriseIdentityStatusResponse":
        return cls(
            feature_enabled=status.feature_enabled,
            sso_provider=status.sso_provider,
            sso_ready=status.sso_ready,
            mfa_mode=status.mfa_mode,
            mfa_ready=status.mfa_ready,
            ready=status.ready,
            blockers=list(status.blockers),
        )


def get_enrollment_service(db: AsyncSession = Depends(get_db)) -> EnterpriseEnrollmentService:
    return EnterpriseEnrollmentService.from_session(db)


@router.get("/status", response_model=EnterpriseIdentityStatusResponse)
async def get_enterprise_status(
    _current_user: User = Depends(get_current_user),
) -> EnterpriseIdentityStatusResponse:
    return EnterpriseIdentityStatusResponse.from_status(get_enterprise_identity_gate_status())


@router.post(
    "/mfa/totp/enroll",
    response_model=TotpEnrollmentStartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_totp_enrollment(
    current_user: User = Depends(get_current_user),
    service: EnterpriseEnrollmentService = Depends(get_enrollment_service),
) -> TotpEnrollmentStartResponse:
    return await service.start_totp_enrollment(current_user)


@router.post("/mfa/totp/confirm", response_model=TotpEnrollmentStatusResponse)
async def confirm_totp_enrollment(
    body: TotpEnrollmentConfirmRequest,
    current_user: User = Depends(get_current_user),
    service: EnterpriseEnrollmentService = Depends(get_enrollment_service),
) -> TotpEnrollmentStatusResponse:
    return await service.confirm_totp_enrollment(current_user, body.code)


@router.get("/mfa/totp", response_model=TotpEnrollmentStatusResponse)
async def get_totp_enrollment_status(
    current_user: User = Depends(get_current_user),
    service: EnterpriseEnrollmentService = Depends(get_enrollment_service),
) -> TotpEnrollmentStatusResponse:
    return await service.get_totp_enrollment_status(current_user)


@router.delete("/mfa/totp", response_model=TotpEnrollmentStatusResponse)
async def disable_totp_enrollment(
    current_user: User = Depends(get_current_user),
    service: EnterpriseEnrollmentService = Depends(get_enrollment_service),
) -> TotpEnrollmentStatusResponse:
    return await service.disable_totp_enrollment(current_user)


@router.post(
    "/sso/enrollment/start",
    response_model=SsoEnrollmentStartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_sso_enrollment(
    current_user: User = Depends(get_current_user),
    service: EnterpriseEnrollmentService = Depends(get_enrollment_service),
) -> SsoEnrollmentStartResponse:
    return await service.start_sso_enrollment(current_user)


@router.post("/sso/enrollment/complete", response_model=SsoEnrollmentCompleteResponse)
async def complete_sso_enrollment(
    body: SsoEnrollmentCompleteRequest,
    current_user: User = Depends(get_current_user),
    service: EnterpriseEnrollmentService = Depends(get_enrollment_service),
) -> SsoEnrollmentCompleteResponse:
    return await service.complete_sso_enrollment(
        current_user,
        code=body.code,
        state=body.state,
    )


@router.get("/sso/enrollment", response_model=SsoEnrollmentStatusResponse)
async def get_sso_enrollment_status(
    current_user: User = Depends(get_current_user),
    service: EnterpriseEnrollmentService = Depends(get_enrollment_service),
) -> SsoEnrollmentStatusResponse:
    return await service.get_sso_enrollment_status(current_user)
