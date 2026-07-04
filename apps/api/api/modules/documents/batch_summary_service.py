"""Batch document LLM summary orchestration service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from verdin_llm_gateway import (
    LlmFeatureDisabledError,
    LlmPiiPolicyError,
    LlmProviderNotConfiguredError,
)

from api.core.batch_llm_summaries import get_batch_llm_summary_status
from api.core.job_queue import JobType, enqueue_job
from api.core.llm import require_llm_gateway
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.documents.batch_summary_models import (
    BatchDocumentSummaryRun,
    BatchSummaryRunStatus,
    BatchSummaryTriggerSource,
)
from api.modules.documents.batch_summary_repository import (
    BatchDocumentSummaryRunListFilters,
    BatchDocumentSummaryRunRepository,
)
from api.modules.documents.batch_summary_schemas import (
    BatchDocumentSummaryEnqueueResponse,
    BatchDocumentSummaryRunListParams,
    BatchDocumentSummaryRunRequest,
    BatchDocumentSummaryRunResponse,
    BatchLlmSummaryStatusResponse,
)
from api.modules.documents.models import Document
from api.modules.documents.permissions import DOCUMENT_READ_ROLE, DOCUMENT_WRITE_ROLE

_BATCH_DOCUMENT_LIMIT = 25


class BatchDocumentSummaryService:
    def __init__(self, repo: BatchDocumentSummaryRunRepository, session: AsyncSession) -> None:
        self._repo = repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> BatchDocumentSummaryService:
        return cls(BatchDocumentSummaryRunRepository(session), session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, DOCUMENT_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view batch document summaries",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, DOCUMENT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to run batch document summaries",
            )

    def _require_llm_ready(self) -> None:
        try:
            require_llm_gateway()
        except LlmFeatureDisabledError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        except LlmProviderNotConfiguredError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        except LlmPiiPolicyError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

    async def get_status(self, user: User) -> BatchLlmSummaryStatusResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        status_value = get_batch_llm_summary_status()
        latest = await self._repo.get_latest_completed_at(organization_id)
        return BatchLlmSummaryStatusResponse(
            enabled=status_value.enabled,
            ready=status_value.ready,
            blockers=list(status_value.blockers),
            last_completed_at=latest.completed_at if latest is not None else None,
        )

    async def _resolve_document_ids(
        self,
        organization_id: uuid.UUID,
        requested_ids: list[uuid.UUID],
    ) -> list[uuid.UUID]:
        if requested_ids:
            result = await self._session.execute(
                select(Document.id).where(
                    Document.organization_id == organization_id,
                    Document.deleted_at.is_(None),
                    Document.id.in_(requested_ids),
                )
            )
            found = list(result.scalars().all())
            if len(found) != len(set(requested_ids)):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or more documents were not found",
                )
            return found

        result = await self._session.execute(
            select(Document.id)
            .where(
                and_(
                    Document.organization_id == organization_id,
                    Document.deleted_at.is_(None),
                    Document.ocr_text.is_not(None),
                )
            )
            .order_by(Document.updated_at.desc())
            .limit(_BATCH_DOCUMENT_LIMIT)
        )
        return list(result.scalars().all())

    async def enqueue_batch_run(
        self,
        user: User,
        body: BatchDocumentSummaryRunRequest,
    ) -> BatchDocumentSummaryEnqueueResponse:
        self._require_write(user)
        self._require_llm_ready()
        organization_id = self._require_organization(user)

        document_ids = await self._resolve_document_ids(organization_id, body.document_ids)
        if not document_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No eligible documents found for batch summarization",
            )

        run = BatchDocumentSummaryRun(
            organization_id=organization_id,
            trigger_source=BatchSummaryTriggerSource.MANUAL,
            status=BatchSummaryRunStatus.PENDING,
            document_ids=[str(document_id) for document_id in document_ids],
            documents_queued=len(document_ids),
            performed_by_user_id=user.id,
        )
        run = await self._repo.create_run(run)
        message = enqueue_job(
            JobType.BATCH_DOCUMENT_LLM_SUMMARY,
            {
                "run_id": str(run.id),
                "organization_id": str(organization_id),
                "document_ids": run.document_ids,
                "performed_by_user_id": str(user.id),
            },
        )
        await self._session.commit()
        return BatchDocumentSummaryEnqueueResponse(
            run=BatchDocumentSummaryRunResponse.from_model(run),
            job_id=message.job_id,
        )

    async def list_runs(
        self,
        user: User,
        params: BatchDocumentSummaryRunListParams,
    ) -> PaginatedResponse[BatchDocumentSummaryRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._repo.list_runs(
            BatchDocumentSummaryRunListFilters(
                organization_id=organization_id,
                skip=skip,
                limit=params.page_size,
            )
        )
        items = [BatchDocumentSummaryRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)
