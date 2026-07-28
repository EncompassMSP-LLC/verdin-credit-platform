"""FAQ/KB retrieval bot endpoints (LRP-405)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.llm.faq_kb_schemas import (
    FaqKbAskRequest,
    FaqKbAskResponse,
    FaqKbConversationTurnResponse,
    FaqKbFeedbackRequest,
)
from api.modules.llm.faq_kb_service import FaqKbService

faq_kb_router = APIRouter(prefix="/faq-kb", tags=["FAQ KB"])


def get_faq_kb_service(db: AsyncSession = Depends(get_db)) -> FaqKbService:
    return FaqKbService.from_session(db)


@faq_kb_router.post("/ask", response_model=FaqKbAskResponse)
async def ask_faq_kb(
    body: FaqKbAskRequest,
    current_user: User = Depends(get_current_user),
    service: FaqKbService = Depends(get_faq_kb_service),
) -> FaqKbAskResponse:
    """Retrieve an audience-aware answer from the approved KB only (LRP-405)."""
    return await service.ask(current_user, body)


@faq_kb_router.get("/conversations", response_model=list[FaqKbConversationTurnResponse])
async def list_faq_kb_conversations(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: FaqKbService = Depends(get_faq_kb_service),
) -> list[FaqKbConversationTurnResponse]:
    return await service.list_turns(current_user, limit=limit)


@faq_kb_router.post(
    "/conversations/{turn_id}/feedback",
    response_model=FaqKbConversationTurnResponse,
)
async def submit_faq_kb_feedback(
    turn_id: uuid.UUID,
    body: FaqKbFeedbackRequest,
    current_user: User = Depends(get_current_user),
    service: FaqKbService = Depends(get_faq_kb_service),
) -> FaqKbConversationTurnResponse:
    return await service.submit_feedback(current_user, turn_id, body)
