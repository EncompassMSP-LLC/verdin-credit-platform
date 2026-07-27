"""Schemas for consultation completed packs (LRP-204)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ConsultationPackSummary(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    generated_at: datetime
    status: str
    schema_version: str
    credit_analysis_run_id: uuid.UUID | None = None


class ConsultationPackResponse(ConsultationPackSummary):
    payload: dict[str, Any]
    disclaimer: str = Field(
        description="Advisory disclaimer; pack never auto-transmits partner notifications."
    )


class ConsultationPackListResponse(BaseModel):
    items: list[ConsultationPackSummary]
