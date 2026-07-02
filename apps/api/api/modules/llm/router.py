"""LLM gateway status endpoints."""

from fastapi import APIRouter, Depends
from verdin_llm_gateway import LlmGateStatus

from api.core.llm import get_llm_gate_status
from api.core.responses import BaseSchema
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User

router = APIRouter(prefix="/llm", tags=["LLM"])


class LlmGateStatusResponse(BaseSchema):
    feature_enabled: bool
    provider_configured: bool
    pii_export_allowed: bool
    provider: str
    model: str | None
    ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: LlmGateStatus) -> "LlmGateStatusResponse":
        return cls(
            feature_enabled=status.feature_enabled,
            provider_configured=status.provider_configured,
            pii_export_allowed=status.pii_export_allowed,
            provider=status.provider,
            model=status.model,
            ready=status.ready,
            blockers=list(status.blockers),
        )


@router.get("/status", response_model=LlmGateStatusResponse)
async def get_llm_status(_current_user: User = Depends(get_current_user)) -> LlmGateStatusResponse:
    return LlmGateStatusResponse.from_status(get_llm_gate_status())
