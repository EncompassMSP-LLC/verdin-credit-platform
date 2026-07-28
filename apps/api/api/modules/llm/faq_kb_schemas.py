"""Schemas for FAQ/KB retrieval bot (LRP-405)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.modules.llm.faq_kb_models import FaqKbAudience, FaqKbFeedbackRating


class FaqKbAskRequest(BaseSchema):
    question: str = Field(min_length=1, max_length=2000)
    audience: FaqKbAudience = FaqKbAudience.STAFF


class FaqKbCitation(BaseSchema):
    article_id: str
    title: str
    source_path: str
    excerpt: str
    score: float


class FaqKbAskResponse(BaseSchema):
    turn_id: uuid.UUID
    question: str
    answer: str
    audience: FaqKbAudience
    grounded: bool
    refused: bool
    refusal_reason: str | None
    citations: list[FaqKbCitation]
    matched_article_ids: list[str]
    disclaimer: str
    created_at: datetime


class FaqKbFeedbackRequest(BaseSchema):
    rating: FaqKbFeedbackRating
    note: str | None = Field(default=None, max_length=2000)


class FaqKbConversationTurnResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    requested_by_user_id: uuid.UUID | None
    audience: FaqKbAudience
    question: str
    answer: str
    grounded: bool
    refused: bool
    refusal_reason: str | None
    citations: list[FaqKbCitation]
    matched_article_ids: list[str]
    disclaimer: str
    feedback_rating: FaqKbFeedbackRating | None
    feedback_note: str | None
    feedback_by_user_id: uuid.UUID | None
    feedback_at: datetime | None
    created_at: datetime
    updated_at: datetime
