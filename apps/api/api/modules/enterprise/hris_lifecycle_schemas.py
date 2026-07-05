"""Pydantic schemas for admin-gated HRIS lifecycle sync scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.hris_lifecycle_sync import HrisLifecycleSyncStatus as LifecycleGateStatus
from api.core.responses import BaseSchema
from api.modules.enterprise.hris_lifecycle_models import (
    HrisLifecycleSyncRun,
    HrisLifecycleSyncRunStatus,
)
from api.modules.enterprise.hris_sync_models import HrisBidirectionalSyncRunKind


class HrisLifecycleSyncStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    hris_sync_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(cls, status: LifecycleGateStatus) -> "HrisLifecycleSyncStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            hris_sync_ready=status.hris_sync_ready,
            blockers=list(status.blockers),
        )


class HrisLifecycleSyncSubmitRequest(BaseSchema):
    lifecycle_summary: str = Field(min_length=1, max_length=2000)


class HrisLifecycleSyncRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    hris_bidirectional_sync_run_id: uuid.UUID
    run_kind: HrisBidirectionalSyncRunKind
    status: HrisLifecycleSyncRunStatus
    lifecycle_summary: str
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: HrisLifecycleSyncRun) -> "HrisLifecycleSyncRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            hris_bidirectional_sync_run_id=run.hris_bidirectional_sync_run_id,
            run_kind=run.run_kind,
            status=run.status,
            lifecycle_summary=run.lifecycle_summary,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
        )


class HrisLifecycleSyncRunResultResponse(BaseSchema):
    completed_at: datetime
    run: HrisLifecycleSyncRunResponse


class HrisLifecycleSyncRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
