"""Pydantic schemas for HRIS bidirectional sync scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.hris_bidirectional_sync import HrisBidirectionalSyncStatus
from api.core.responses import BaseSchema
from api.modules.enterprise.hris_sync_models import (
    HrisBidirectionalSyncRun,
    HrisBidirectionalSyncRunKind,
    HrisBidirectionalSyncRunStatus,
    HrisBidirectionalSyncTriggerSource,
)


class HrisBidirectionalSyncStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    saml_metadata_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: HrisBidirectionalSyncStatus
    ) -> "HrisBidirectionalSyncStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            saml_metadata_ready=status.saml_metadata_ready,
            blockers=list(status.blockers),
        )


class HrisBidirectionalSyncRunRequest(BaseSchema):
    run_kind: HrisBidirectionalSyncRunKind = HrisBidirectionalSyncRunKind.EMPLOYEES_INBOUND


class HrisBidirectionalSyncRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    run_kind: HrisBidirectionalSyncRunKind
    trigger_source: HrisBidirectionalSyncTriggerSource
    status: HrisBidirectionalSyncRunStatus
    records_synced: int
    records_skipped: int
    performed_by_user_id: uuid.UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(cls, run: HrisBidirectionalSyncRun) -> "HrisBidirectionalSyncRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            run_kind=run.run_kind,
            trigger_source=run.trigger_source,
            status=run.status,
            records_synced=run.records_synced,
            records_skipped=run.records_skipped,
            performed_by_user_id=run.performed_by_user_id,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
        )


class HrisBidirectionalSyncRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class HrisBidirectionalSyncRunResultResponse(BaseSchema):
    completed_at: datetime
    run: HrisBidirectionalSyncRunResponse
