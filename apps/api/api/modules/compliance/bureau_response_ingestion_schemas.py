"""Schemas for bureau response ingestion audit scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.modules.compliance.bureau_response_ingestion_models import (
    BureauResponseIngestionRun,
    BureauResponseIngestionRunStatus,
)

LIVE_POLLING_BLOCKER = (
    "Live bureau response polling is deferred to 17.0+ "
    "(requires live bureau API access + legal/compliance sign-off)"
)


class BureauResponseIngestionStatusResponse(BaseSchema):
    enabled: bool = True
    ready: bool = False
    live_polling_enabled: bool = False
    blockers: list[str] = Field(default_factory=lambda: [LIVE_POLLING_BLOCKER])


class BureauResponseIngestionStartRequest(BaseSchema):
    summary: str = Field(min_length=1, max_length=2000)
    bureau_target: str = Field(default="all", min_length=1, max_length=32)
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None


class BureauResponseIngestionRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    case_id: uuid.UUID | None
    account_id: uuid.UUID | None
    bureau_target: str
    status: BureauResponseIngestionRunStatus
    summary: str
    deferral_reason: str
    requested_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: BureauResponseIngestionRun) -> "BureauResponseIngestionRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            case_id=run.case_id,
            account_id=run.account_id,
            bureau_target=run.bureau_target,
            status=run.status,
            summary=run.summary,
            deferral_reason=run.deferral_reason,
            requested_by_user_id=run.requested_by_user_id,
            requested_at=run.requested_at,
            error_message=run.error_message,
        )


class BureauResponseIngestionRunResultResponse(BaseSchema):
    completed_at: datetime
    run: BureauResponseIngestionRunResponse


class BureauResponseIngestionRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
