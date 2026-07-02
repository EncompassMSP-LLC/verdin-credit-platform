"""Cases domain schemas."""

import uuid
from datetime import datetime
from typing import Literal, Self

from pydantic import EmailStr, Field, model_validator

from api.core.pagination import PaginationParams
from api.core.responses import BaseSchema
from api.modules.cases.models import Case, CasePriority, CaseStage, CaseStatus

CaseSortField = Literal[
    "created_at",
    "updated_at",
    "title",
    "status",
    "stage",
    "priority",
    "opened_at",
    "case_number",
]
CaseSortOrder = Literal["asc", "desc"]


class CaseCreate(BaseSchema):
    title: str = Field(min_length=1, max_length=255)
    client_id: uuid.UUID | None = None
    client_name: str | None = Field(default=None, min_length=1, max_length=255)
    client_email: EmailStr | None = None
    case_number: str | None = Field(default=None, max_length=50)
    status: CaseStatus = CaseStatus.OPEN
    stage: CaseStage = CaseStage.INTAKE
    priority: CasePriority = CasePriority.MEDIUM
    assigned_user_id: uuid.UUID | None = None
    summary: str | None = None
    notes: str | None = None
    opened_at: datetime | None = None

    @model_validator(mode="after")
    def require_client_identity(self) -> Self:
        if self.client_id is None and not self.client_name:
            raise ValueError("Either client_id or client_name is required")
        return self


class CaseUpdate(BaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    client_id: uuid.UUID | None = None
    client_name: str | None = Field(default=None, min_length=1, max_length=255)
    client_email: EmailStr | None = None
    case_number: str | None = Field(default=None, max_length=50)
    status: CaseStatus | None = None
    stage: CaseStage | None = None
    priority: CasePriority | None = None
    assigned_user_id: uuid.UUID | None = None
    summary: str | None = None
    notes: str | None = None
    opened_at: datetime | None = None
    closed_at: datetime | None = None


class CaseListParams(PaginationParams):
    search: str | None = Field(default=None, max_length=255)
    status: CaseStatus | None = None
    stage: CaseStage | None = None
    priority: CasePriority | None = None
    assigned_user_id: uuid.UUID | None = None
    client_id: uuid.UUID | None = None
    sort_by: CaseSortField = "created_at"
    sort_order: CaseSortOrder = "desc"


class CaseResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    client_id: uuid.UUID | None
    case_number: str | None
    title: str
    client_name: str
    client_email: str | None
    status: CaseStatus
    stage: CaseStage
    priority: CasePriority
    assigned_user_id: uuid.UUID | None
    summary: str | None
    notes: str | None
    opened_at: datetime
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    created_by_id: uuid.UUID | None
    updated_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, case: Case) -> "CaseResponse":
        return cls(
            id=case.id,
            organization_id=case.organization_id,
            client_id=case.client_id,
            case_number=case.case_number,
            title=case.title,
            client_name=case.client_name,
            client_email=case.client_email,
            status=case.status,
            stage=case.stage,
            priority=case.priority,
            assigned_user_id=case.assigned_to_id,
            summary=case.summary,
            notes=case.notes,
            opened_at=case.opened_at,
            closed_at=case.closed_at,
            created_at=case.created_at,
            updated_at=case.updated_at,
            deleted_at=case.deleted_at,
            created_by_id=case.created_by_id,
            updated_by_id=case.updated_by_id,
        )
