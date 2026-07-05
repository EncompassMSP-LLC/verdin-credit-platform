"""LLM gateway and agent observability endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from verdin_llm_gateway import LlmGateStatus

from api.core.llm import get_llm_gate_status
from api.core.responses import BaseSchema
from api.database.session import get_db
from api.modules.accounts.dispute_draft_augment_dependencies import (
    require_llm_dispute_draft_augment_enabled,
)
from api.modules.accounts.dispute_draft_augment_schemas import (
    LlmDisputeDraftAugmentStatusResponse,
)
from api.modules.accounts.dispute_draft_augment_service import LlmDisputeDraftAugmentService
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.llm.agent_arbitrary_execution_router import agent_arbitrary_execution_router
from api.modules.llm.agent_execution_router import agent_execution_router
from api.modules.llm.agent_observability_router import agent_observability_router
from api.modules.llm.agent_supervised_loop_router import agent_supervised_loop_router
from api.modules.llm.agent_tool_calling_router import agent_tool_calling_router
from api.modules.llm.agent_unsupervised_loop_router import agent_unsupervised_loop_router

router = APIRouter(prefix="/llm", tags=["LLM"])
router.include_router(agent_observability_router)
router.include_router(agent_execution_router)
router.include_router(agent_tool_calling_router)
router.include_router(agent_supervised_loop_router)
router.include_router(agent_unsupervised_loop_router)
router.include_router(agent_arbitrary_execution_router)


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


def get_llm_dispute_draft_augment_service(
    db: AsyncSession = Depends(get_db),
) -> LlmDisputeDraftAugmentService:
    return LlmDisputeDraftAugmentService.from_session(db)


@router.get("/dispute-draft/status", response_model=LlmDisputeDraftAugmentStatusResponse)
async def get_llm_dispute_draft_augment_status(
    _: None = Depends(require_llm_dispute_draft_augment_enabled),
    service: LlmDisputeDraftAugmentService = Depends(get_llm_dispute_draft_augment_service),
) -> LlmDisputeDraftAugmentStatusResponse:
    return service.get_status_response()
