"""FAQ/KB retrieval service (LRP-405)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.llm.faq_kb_models import FaqKbConversationTurn
from api.modules.llm.faq_kb_repository import FaqKbRepository
from api.modules.llm.faq_kb_retrieval import Citation, retrieve_faq_answer
from api.modules.llm.faq_kb_schemas import (
    FaqKbAskRequest,
    FaqKbAskResponse,
    FaqKbCitation,
    FaqKbConversationTurnResponse,
    FaqKbFeedbackRequest,
)


class FaqKbService:
    def __init__(self, repo: FaqKbRepository, session: AsyncSession | None = None) -> None:
        self._repo = repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> FaqKbService:
        return cls(FaqKbRepository(session), session=session)

    def _require_org(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_staff_feedback(self, user: User) -> None:
        if not has_permission(user.role, UserRole.CASE_MANAGER):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit FAQ feedback",
            )

    @staticmethod
    def _citations_payload(result_citations: tuple[Citation, ...]) -> list[dict[str, object]]:
        return [
            {
                "article_id": c.article_id,
                "title": c.title,
                "source_path": c.source_path,
                "excerpt": c.excerpt,
                "score": c.score,
            }
            for c in result_citations
        ]

    def _to_ask_response(self, turn: FaqKbConversationTurn) -> FaqKbAskResponse:
        return FaqKbAskResponse(
            turn_id=turn.id,
            question=turn.question,
            answer=turn.answer,
            audience=turn.audience,
            grounded=turn.grounded,
            refused=turn.refused,
            refusal_reason=turn.refusal_reason,
            citations=[FaqKbCitation.model_validate(item) for item in turn.citations],
            matched_article_ids=list(turn.matched_article_ids or []),
            disclaimer=turn.disclaimer,
            created_at=turn.created_at,
        )

    def _to_turn_response(self, turn: FaqKbConversationTurn) -> FaqKbConversationTurnResponse:
        return FaqKbConversationTurnResponse(
            id=turn.id,
            organization_id=turn.organization_id,
            requested_by_user_id=turn.requested_by_user_id,
            audience=turn.audience,
            question=turn.question,
            answer=turn.answer,
            grounded=turn.grounded,
            refused=turn.refused,
            refusal_reason=turn.refusal_reason,
            citations=[FaqKbCitation.model_validate(item) for item in turn.citations],
            matched_article_ids=list(turn.matched_article_ids or []),
            disclaimer=turn.disclaimer,
            feedback_rating=turn.feedback_rating,
            feedback_note=turn.feedback_note,
            feedback_by_user_id=turn.feedback_by_user_id,
            feedback_at=turn.feedback_at,
            created_at=turn.created_at,
            updated_at=turn.updated_at,
        )

    async def ask(self, user: User, body: FaqKbAskRequest) -> FaqKbAskResponse:
        organization_id = self._require_org(user)
        result = retrieve_faq_answer(question=body.question, audience=body.audience.value)
        turn = FaqKbConversationTurn(
            organization_id=organization_id,
            requested_by_user_id=user.id,
            audience=body.audience,
            question=body.question.strip(),
            answer=result.answer,
            grounded=result.grounded,
            refused=result.refused,
            refusal_reason=result.refusal_reason,
            citations=self._citations_payload(result.citations),
            matched_article_ids=list(result.matched_article_ids),
            disclaimer=result.disclaimer,
        )
        await self._repo.add(turn)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(turn)
        return self._to_ask_response(turn)

    async def list_turns(
        self,
        user: User,
        *,
        limit: int = 50,
    ) -> list[FaqKbConversationTurnResponse]:
        organization_id = self._require_org(user)
        turns = await self._repo.list_for_org(organization_id=organization_id, limit=limit)
        return [self._to_turn_response(turn) for turn in turns]

    async def submit_feedback(
        self,
        user: User,
        turn_id: uuid.UUID,
        body: FaqKbFeedbackRequest,
    ) -> FaqKbConversationTurnResponse:
        self._require_staff_feedback(user)
        organization_id = self._require_org(user)
        turn = await self._repo.get_by_id(turn_id, organization_id=organization_id)
        if turn is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation turn not found"
            )
        turn.feedback_rating = body.rating
        turn.feedback_note = body.note
        turn.feedback_by_user_id = user.id
        turn.feedback_at = datetime.now(UTC)
        await self._repo.save(turn)
        if self._session is not None:
            await self._session.commit()
            await self._session.refresh(turn)
        return self._to_turn_response(turn)
