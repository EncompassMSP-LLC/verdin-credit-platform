"""Pydantic schemas for admin-gated unredacted cross-org benchmark export scaffold."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.responses import BaseSchema
from api.core.unredacted_cross_org_benchmark_export import (
    UnredactedCrossOrgBenchmarkExportStatus as ExportGateStatus,
)
from api.modules.reporting.unredacted_cross_org_benchmark_export_models import (
    UnredactedCrossOrgBenchmarkExportRun,
    UnredactedCrossOrgBenchmarkExportRunStatus,
)


class UnredactedCrossOrgBenchmarkExportStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    cross_org_benchmark_ready: bool
    blockers: list[str]

    @classmethod
    def from_status(
        cls, status: ExportGateStatus
    ) -> "UnredactedCrossOrgBenchmarkExportStatusResponse":
        return cls(
            enabled=status.enabled,
            ready=status.ready,
            cross_org_benchmark_ready=status.cross_org_benchmark_ready,
            blockers=list(status.blockers),
        )


class UnredactedCrossOrgBenchmarkExportSubmitRequest(BaseSchema):
    export_summary: str = Field(min_length=1, max_length=2000)
    export_reference_id: str | None = Field(default=None, max_length=255)


class UnredactedCrossOrgBenchmarkExportRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    cross_org_benchmark_run_id: uuid.UUID
    status: UnredactedCrossOrgBenchmarkExportRunStatus
    export_summary: str
    export_reference_id: str | None
    requested_by_user_id: uuid.UUID | None
    approved_by_user_id: uuid.UUID | None
    requested_at: datetime | None
    approved_at: datetime | None
    error_message: str | None

    @classmethod
    def from_model(
        cls, run: UnredactedCrossOrgBenchmarkExportRun
    ) -> "UnredactedCrossOrgBenchmarkExportRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            cross_org_benchmark_run_id=run.cross_org_benchmark_run_id,
            status=run.status,
            export_summary=run.export_summary,
            export_reference_id=run.export_reference_id,
            requested_by_user_id=run.requested_by_user_id,
            approved_by_user_id=run.approved_by_user_id,
            requested_at=run.requested_at,
            approved_at=run.approved_at,
            error_message=run.error_message,
        )


class UnredactedCrossOrgBenchmarkExportRunResultResponse(BaseSchema):
    completed_at: datetime
    run: UnredactedCrossOrgBenchmarkExportRunResponse


class UnredactedCrossOrgBenchmarkExportRunListParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
