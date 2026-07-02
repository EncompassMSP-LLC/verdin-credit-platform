"""Enterprise identity readiness endpoints."""

from fastapi import APIRouter, Depends

from api.core.enterprise import get_enterprise_identity_gate_status
from api.core.enterprise_identity import EnterpriseIdentityStatus
from api.core.responses import BaseSchema
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User

router = APIRouter(prefix="/enterprise", tags=["Enterprise"])


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


@router.get("/status", response_model=EnterpriseIdentityStatusResponse)
async def get_enterprise_status(
    _current_user: User = Depends(get_current_user),
) -> EnterpriseIdentityStatusResponse:
    return EnterpriseIdentityStatusResponse.from_status(get_enterprise_identity_gate_status())
