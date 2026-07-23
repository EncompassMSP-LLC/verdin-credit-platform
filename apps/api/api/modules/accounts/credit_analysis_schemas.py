"""Schemas for credit analysis runs and portal readiness."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CreditAnalysisRunSummary(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    generated_at: datetime
    reports_evaluated: int
    tradelines_evaluated: int
    borrower_readiness_score: int
    mortgage_readiness_score: int
    schema_version: str
    band: str
    status: str


class CreditAnalysisRunResponse(CreditAnalysisRunSummary):
    payload: dict[str, Any]
    formula_version: str
    score_version: str
    inputs_hash: str
    published_at: datetime | None = None


class CreditAnalysisRunListResponse(BaseModel):
    items: list[CreditAnalysisRunSummary]


class PortalReadinessDimension(BaseModel):
    key: str
    label: str
    score: int
    weight: float


class PortalReadinessBlocker(BaseModel):
    id: str
    title: str
    impact: str
    action: str


class PortalReadinessAccount(BaseModel):
    id: str
    creditor_label: str
    bureau: str
    readiness_score: int | None
    risk_score: int | None
    dispute_status: str
    recommended_action: str | None


class PortalCaseReadinessResponse(BaseModel):
    case_id: uuid.UUID
    overall: int = Field(description="Staff numeric; borrower UI should prefer band")
    band: str
    updated_at: datetime
    trend: int | None = None
    disclaimer: str
    dimensions: list[PortalReadinessDimension]
    blockers: list[PortalReadinessBlocker]
    accounts: list[PortalReadinessAccount]
