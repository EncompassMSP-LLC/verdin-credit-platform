"""Batch document LLM summary schemas."""

import uuid
from datetime import datetime

from pydantic import Field

from api.core.pagination import PaginationParams
from api.core.responses import BaseSchema
from api.modules.documents.batch_summary_models import BatchDocumentSummaryRun


class BatchLlmSummaryStatusResponse(BaseSchema):
    enabled: bool
    ready: bool
    blockers: list[str]
    last_completed_at: datetime | None


class BatchDocumentSummaryRunRequest(BaseSchema):
    document_ids: list[uuid.UUID] = Field(default_factory=list)


class BatchDocumentSummaryRunResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    trigger_source: str
    status: str
    document_ids: list[str]
    documents_queued: int
    documents_succeeded: int
    documents_failed: int
    performed_by_user_id: uuid.UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    created_at: datetime

    @classmethod
    def from_model(cls, run: BatchDocumentSummaryRun) -> "BatchDocumentSummaryRunResponse":
        return cls(
            id=run.id,
            organization_id=run.organization_id,
            trigger_source=run.trigger_source.value,
            status=run.status.value,
            document_ids=list(run.document_ids),
            documents_queued=run.documents_queued,
            documents_succeeded=run.documents_succeeded,
            documents_failed=run.documents_failed,
            performed_by_user_id=run.performed_by_user_id,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
            created_at=run.created_at,
        )


class BatchDocumentSummaryRunListParams(PaginationParams):
    pass


class BatchDocumentSummaryEnqueueResponse(BaseSchema):
    run: BatchDocumentSummaryRunResponse
    job_id: str
