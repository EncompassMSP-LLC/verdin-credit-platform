"""Pydantic schemas for live unredacted benchmark blob export scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.live_unredacted_benchmark_blob_export import (
    LiveUnredactedBenchmarkBlobExportStatus as BlobGateStatus,
)
from api.core.responses import BaseSchema
from api.modules.reporting.live_unredacted_benchmark_blob_export_models import (
    LiveUnredactedBenchmarkBlobExportRun,
    LiveUnredactedBenchmarkBlobExportRunStatus,
)


class LiveUnredactedBenchmarkBlobExportStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    unredacted_export_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: BlobGateStatus
    ) -> "LiveUnredactedBenchmarkBlobExportStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            unredacted_export_ready=status.unredacted_export_ready,
            blockers=list(status.blockers),
        )


class LiveUnredactedBenchmarkBlobExportSubmitRequest(BaseSchema):
    export_summary: str = Field(min_length=1, max_length=2000)


class LiveUnredactedBenchmarkBlobExportRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    unredacted_export_run_id: uuid.UUID
    status: LiveUnredactedBenchmarkBlobExportRunStatus
    export_summary: str
    storage_key: str | None
    content_type: str | None
    byte_size: int | None
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    exported_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(
        cls, run: LiveUnredactedBenchmarkBlobExportRun
    ) -> "LiveUnredactedBenchmarkBlobExportRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            unredacted_export_run_id=run.unredacted_export_run_id,
            status=run.status,
            export_summary=run.export_summary,
            storage_key=run.storage_key,
            content_type=run.content_type,
            byte_size=run.byte_size,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            exported_at=run.exported_at,
            error_message=run.error_message,
        )


class LiveUnredactedBenchmarkBlobExportRunResultResponse(BaseSchema):
    completed_at: datetime
    run: LiveUnredactedBenchmarkBlobExportRunResponse


class LiveUnredactedBenchmarkBlobExportRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
