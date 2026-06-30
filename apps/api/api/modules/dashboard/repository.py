"""Dashboard repository — Mission Control aggregation queries."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from api.modules.accounts.models import Account, AccountStatus
from api.modules.cases.models import Case, CasePriority, CaseStatus
from api.modules.documents.constants import (
    DocumentProcessingStatus,
    MetadataStatus,
    ResolutionStatus,
)
from api.modules.documents.metadata_models import DocumentEntityResolution, DocumentMetadata
from api.modules.documents.models import Document
from api.modules.tasks.models import Task, TaskPriority, TaskStatus
from api.modules.timeline.models import TimelineEvent

_TERMINAL_TASK_STATUSES = (TaskStatus.COMPLETED, TaskStatus.CANCELED)
_OPEN_CASE_STATUSES = (CaseStatus.OPEN, CaseStatus.ACTIVE)
_CLOSED_CASE_STATUSES = (CaseStatus.RESOLVED, CaseStatus.CLOSED)
_HIGH_PRIORITIES = (CasePriority.HIGH, CasePriority.CRITICAL)
_HIGH_TASK_PRIORITIES = (TaskPriority.HIGH, TaskPriority.CRITICAL)
_PROCESSING_ACTIVE = (
    DocumentProcessingStatus.PENDING,
    DocumentProcessingStatus.QUEUED,
    DocumentProcessingStatus.PROCESSING,
)
_OCR_QUEUE_STATUSES = (DocumentProcessingStatus.QUEUED, DocumentProcessingStatus.PROCESSING)
_RESOLVED_ENTITY_STATUSES = (ResolutionStatus.MATCHED, ResolutionStatus.CONFIRMED)
_UNRESOLVED_ENTITY_STATUSES = (ResolutionStatus.AMBIGUOUS, ResolutionStatus.UNMATCHED)


class DashboardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_snapshot(self, organization_id: uuid.UUID) -> dict[str, Any]:
        now = datetime.now(UTC)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        cases = await self._get_cases_metrics(organization_id, start_of_day, end_of_day)
        accounts = await self._get_accounts_metrics(organization_id)
        documents = await self._get_documents_metrics(organization_id)
        tasks = await self._get_tasks_metrics(organization_id, now, start_of_day, end_of_day)
        processing = await self._get_processing(organization_id)
        performance = await self._get_performance(
            organization_id, start_of_day, end_of_day, cases["average_resolution_time_hours"]
        )
        timeline = await self._get_timeline(organization_id)
        alerts = await self._get_alerts(organization_id, now)

        overview = {
            "open_cases": cases["open"],
            "active_accounts": accounts["active"],
            "documents": documents["total"],
            "tasks_due_today": tasks["due_today"],
            "overdue_tasks": tasks["overdue"],
            "alert_count": alerts["total"],
        }

        return {
            "overview": overview,
            "cases": cases,
            "accounts": accounts,
            "documents": documents,
            "timeline": timeline,
            "tasks": tasks,
            "processing": processing,
            "performance": performance,
            "alerts": alerts,
        }

    async def _count(self, query: Any) -> int:
        result = await self._session.execute(select(func.count()).select_from(query.subquery()))
        return int(result.scalar_one())

    async def _avg_resolution_hours(self, organization_id: uuid.UUID) -> float | None:
        result = await self._session.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        Case.closed_at - Case.opened_at,
                    )
                )
            ).where(
                Case.organization_id == organization_id,
                Case.deleted_at.is_(None),
                Case.closed_at.isnot(None),
                Case.opened_at.isnot(None),
            )
        )
        avg_seconds = result.scalar_one()
        return round(float(avg_seconds) / 3600, 1) if avg_seconds is not None else None

    async def _get_cases_metrics(
        self,
        organization_id: uuid.UUID,
        start_of_day: datetime,
        end_of_day: datetime,
    ) -> dict[str, Any]:
        base = and_(Case.organization_id == organization_id, Case.deleted_at.is_(None))

        return {
            "open": await self._count(
                select(Case).where(base, Case.status.in_(_OPEN_CASE_STATUSES))
            ),
            "high_priority": await self._count(
                select(Case).where(
                    base,
                    Case.status.in_(_OPEN_CASE_STATUSES),
                    Case.priority.in_(_HIGH_PRIORITIES),
                )
            ),
            "created_today": await self._count(
                select(Case).where(
                    base, Case.opened_at >= start_of_day, Case.opened_at < end_of_day
                )
            ),
            "closed_today": await self._count(
                select(Case).where(
                    base,
                    Case.closed_at.isnot(None),
                    Case.closed_at >= start_of_day,
                    Case.closed_at < end_of_day,
                    Case.status.in_(_CLOSED_CASE_STATUSES),
                )
            ),
            "average_resolution_time_hours": await self._avg_resolution_hours(organization_id),
        }

    async def _get_accounts_metrics(self, organization_id: uuid.UUID) -> dict[str, Any]:
        base = and_(Account.organization_id == organization_id, Account.deleted_at.is_(None))

        active = await self._count(
            select(Account).where(base, Account.account_status == AccountStatus.OPEN)
        )
        total = await self._count(select(Account).where(base))

        cases_with_accounts = int(
            (
                await self._session.execute(
                    select(func.count(func.distinct(Account.case_id))).where(base)
                )
            ).scalar_one()
            or 0
        )

        return {
            "active": active,
            "total": total,
            "per_case": round(total / cases_with_accounts, 1) if cases_with_accounts > 0 else 0.0,
        }

    async def _get_documents_metrics(self, organization_id: uuid.UUID) -> dict[str, Any]:
        base_doc = and_(
            Document.organization_id == organization_id,
            Document.deleted_at.is_(None),
        )

        total = await self._count(select(Document).where(base_doc))
        processing = await self._count(
            select(Document).where(base_doc, Document.processing_status.in_(_PROCESSING_ACTIVE))
        )

        classification_conf_result = await self._session.execute(
            select(func.avg(Document.confidence_score)).where(
                base_doc,
                Document.document_type.isnot(None),
                Document.confidence_score.isnot(None),
            )
        )
        classification_conf = classification_conf_result.scalar_one()
        classification_confidence = (
            round(float(classification_conf), 3) if classification_conf is not None else None
        )

        entity_conf_result = await self._session.execute(
            select(func.avg(DocumentEntityResolution.confidence_score)).where(
                DocumentEntityResolution.organization_id == organization_id,
            )
        )
        entity_conf = entity_conf_result.scalar_one()
        entity_resolution_confidence = (
            round(float(entity_conf), 3) if entity_conf is not None else None
        )

        ai_ready_q = (
            select(Document)
            .join(DocumentMetadata, DocumentMetadata.document_id == Document.id)
            .join(DocumentEntityResolution, DocumentEntityResolution.document_id == Document.id)
            .where(
                base_doc,
                Document.document_type.isnot(None),
                DocumentMetadata.metadata_status == MetadataStatus.EXTRACTED,
                DocumentEntityResolution.resolution_status.in_(_RESOLVED_ENTITY_STATUSES),
            )
            .distinct()
        )

        unresolved_q = (
            select(Document)
            .join(
                DocumentEntityResolution,
                DocumentEntityResolution.document_id == Document.id,
            )
            .where(
                base_doc,
                DocumentEntityResolution.resolution_status.in_(_UNRESOLVED_ENTITY_STATUSES),
            )
            .distinct()
        )

        return {
            "total": total,
            "processing": processing,
            "classification_confidence": classification_confidence,
            "entity_resolution_confidence": entity_resolution_confidence,
            "ai_ready": await self._count(ai_ready_q),
            "unresolved": await self._count(unresolved_q),
        }

    async def _get_tasks_metrics(
        self,
        organization_id: uuid.UUID,
        now: datetime,
        start_of_day: datetime,
        end_of_day: datetime,
    ) -> dict[str, int]:
        base = and_(
            Task.organization_id == organization_id,
            Task.deleted_at.is_(None),
            Task.status.notin_(_TERMINAL_TASK_STATUSES),
        )

        return {
            "pending": await self._count(select(Task).where(base)),
            "due_today": await self._count(
                select(Task).where(
                    base,
                    Task.due_date.isnot(None),
                    Task.due_date >= start_of_day,
                    Task.due_date < end_of_day,
                )
            ),
            "overdue": await self._count(
                select(Task).where(
                    base,
                    Task.due_date.isnot(None),
                    Task.due_date < now,
                )
            ),
        }

    async def _get_processing(self, organization_id: uuid.UUID) -> dict[str, int]:
        base_doc = and_(
            Document.organization_id == organization_id,
            Document.deleted_at.is_(None),
        )

        ocr_queue_q = select(Document).where(
            base_doc,
            Document.processing_status.in_(_OCR_QUEUE_STATUSES),
        )
        ocr_failed_q = select(Document).where(
            base_doc,
            Document.processing_status == DocumentProcessingStatus.FAILED,
        )
        classification_pending_q = select(Document).where(
            base_doc,
            Document.processing_status == DocumentProcessingStatus.COMPLETED,
            Document.document_type.is_(None),
        )
        metadata_pending_q = (
            select(Document)
            .outerjoin(DocumentMetadata, DocumentMetadata.document_id == Document.id)
            .where(
                base_doc,
                Document.document_type.isnot(None),
                or_(
                    DocumentMetadata.id.is_(None),
                    DocumentMetadata.metadata_status == MetadataStatus.PENDING,
                ),
            )
        )
        entity_resolution_pending_q = (
            select(Document)
            .join(DocumentMetadata, DocumentMetadata.document_id == Document.id)
            .where(
                base_doc,
                DocumentMetadata.metadata_status == MetadataStatus.EXTRACTED,
                or_(
                    ~exists(
                        select(DocumentEntityResolution.id).where(
                            DocumentEntityResolution.document_id == Document.id,
                        )
                    ),
                    exists(
                        select(DocumentEntityResolution.id).where(
                            DocumentEntityResolution.document_id == Document.id,
                            DocumentEntityResolution.resolution_status.in_(
                                _UNRESOLVED_ENTITY_STATUSES
                            ),
                        )
                    ),
                ),
            )
        )

        return {
            "ocr_queue": await self._count(ocr_queue_q),
            "ocr_failed": await self._count(ocr_failed_q),
            "classification_pending": await self._count(classification_pending_q),
            "metadata_pending": await self._count(metadata_pending_q),
            "entity_resolution_pending": await self._count(entity_resolution_pending_q),
        }

    async def _get_performance(
        self,
        organization_id: uuid.UUID,
        start_of_day: datetime,
        end_of_day: datetime,
        average_resolution_time_hours: float | None,
    ) -> dict[str, Any]:
        base_case = and_(Case.organization_id == organization_id, Case.deleted_at.is_(None))
        base_doc = and_(
            Document.organization_id == organization_id,
            Document.deleted_at.is_(None),
        )
        base_account = and_(
            Account.organization_id == organization_id,
            Account.deleted_at.is_(None),
        )

        total_documents = int(
            (await self._session.execute(select(func.count()).where(base_doc))).scalar_one() or 0
        )
        total_accounts = int(
            (await self._session.execute(select(func.count()).where(base_account))).scalar_one()
            or 0
        )
        cases_with_documents = int(
            (
                await self._session.execute(
                    select(func.count(func.distinct(Document.case_id))).where(
                        base_doc,
                        Document.case_id.isnot(None),
                    )
                )
            ).scalar_one()
            or 0
        )
        cases_with_accounts = int(
            (
                await self._session.execute(
                    select(func.count(func.distinct(Account.case_id))).where(base_account)
                )
            ).scalar_one()
            or 0
        )

        return {
            "cases_created_today": await self._count(
                select(Case).where(
                    base_case,
                    Case.opened_at >= start_of_day,
                    Case.opened_at < end_of_day,
                )
            ),
            "cases_closed_today": await self._count(
                select(Case).where(
                    base_case,
                    Case.closed_at.isnot(None),
                    Case.closed_at >= start_of_day,
                    Case.closed_at < end_of_day,
                    Case.status.in_(_CLOSED_CASE_STATUSES),
                )
            ),
            "average_resolution_time_hours": average_resolution_time_hours,
            "documents_per_case": round(total_documents / cases_with_documents, 1)
            if cases_with_documents > 0
            else 0.0,
            "accounts_per_case": round(total_accounts / cases_with_accounts, 1)
            if cases_with_accounts > 0
            else 0.0,
        }

    async def _get_timeline(self, organization_id: uuid.UUID) -> list[dict[str, Any]]:
        CaseAlias = aliased(Case)
        DocumentAlias = aliased(Document)
        result = await self._session.execute(
            select(
                TimelineEvent, CaseAlias.case_number, DocumentAlias.title, DocumentAlias.file_name
            )
            .outerjoin(CaseAlias, CaseAlias.id == TimelineEvent.case_id)
            .outerjoin(DocumentAlias, DocumentAlias.id == TimelineEvent.document_id)
            .where(TimelineEvent.organization_id == organization_id)
            .order_by(TimelineEvent.occurred_at.desc())
            .limit(15)
        )
        return [
            {
                "id": row.TimelineEvent.id,
                "occurred_at": row.TimelineEvent.occurred_at,
                "event_type": row.TimelineEvent.event_type,
                "title": row.TimelineEvent.title,
                "description": row.TimelineEvent.description,
                "case_id": row.TimelineEvent.case_id,
                "case_number": row.case_number,
                "document_id": row.TimelineEvent.document_id,
                "document_title": row.title,
                "file_name": row.file_name,
                "metadata": dict(row.TimelineEvent.event_metadata or {}),
            }
            for row in result.all()
        ]

    async def _get_alerts(self, organization_id: uuid.UUID, now: datetime) -> dict[str, Any]:
        items: list[dict[str, Any]] = []

        ocr_failed_result = await self._session.execute(
            select(Document, Case.case_number)
            .outerjoin(Case, Case.id == Document.case_id)
            .where(
                Document.organization_id == organization_id,
                Document.deleted_at.is_(None),
                Document.processing_status == DocumentProcessingStatus.FAILED,
            )
            .order_by(Document.updated_at.desc())
            .limit(6)
        )
        for ocr_row in ocr_failed_result.all():
            items.append(
                {
                    "id": f"ocr-failure-{ocr_row.Document.id}",
                    "alert_type": "ocr_failure",
                    "severity": "high",
                    "title": "OCR failure",
                    "message": ocr_row.Document.ocr_error or ocr_row.Document.file_name,
                    "entity_type": "document",
                    "entity_id": ocr_row.Document.id,
                    "case_id": ocr_row.Document.case_id,
                    "case_number": ocr_row.case_number,
                }
            )

        unresolved_result = await self._session.execute(
            select(Document, Case.case_number)
            .join(
                DocumentEntityResolution,
                DocumentEntityResolution.document_id == Document.id,
            )
            .outerjoin(Case, Case.id == Document.case_id)
            .where(
                Document.organization_id == organization_id,
                Document.deleted_at.is_(None),
                DocumentEntityResolution.resolution_status.in_(_UNRESOLVED_ENTITY_STATUSES),
            )
            .order_by(Document.updated_at.desc())
            .limit(6)
        )
        for unresolved_row in unresolved_result.all():
            items.append(
                {
                    "id": f"unmatched-entity-{unresolved_row.Document.id}",
                    "alert_type": "unmatched_entity",
                    "severity": "medium",
                    "title": "Unmatched entity",
                    "message": unresolved_row.Document.file_name,
                    "entity_type": "document",
                    "entity_id": unresolved_row.Document.id,
                    "case_id": unresolved_row.Document.case_id,
                    "case_number": unresolved_row.case_number,
                }
            )

        review_result = await self._session.execute(
            select(Document, Case.case_number)
            .join(
                DocumentEntityResolution,
                DocumentEntityResolution.document_id == Document.id,
            )
            .outerjoin(Case, Case.id == Document.case_id)
            .where(
                Document.organization_id == organization_id,
                Document.deleted_at.is_(None),
                DocumentEntityResolution.resolution_status == ResolutionStatus.AMBIGUOUS,
            )
            .order_by(Document.updated_at.desc())
            .limit(6)
        )
        for review_row in review_result.all():
            items.append(
                {
                    "id": f"document-review-{review_row.Document.id}",
                    "alert_type": "document_review",
                    "severity": "medium",
                    "title": "Document requires review",
                    "message": review_row.Document.title,
                    "entity_type": "document",
                    "entity_id": review_row.Document.id,
                    "case_id": review_row.Document.case_id,
                    "case_number": review_row.case_number,
                }
            )

        overdue_result = await self._session.execute(
            select(Task, Case.case_number)
            .outerjoin(Case, Case.id == Task.case_id)
            .where(
                Task.organization_id == organization_id,
                Task.deleted_at.is_(None),
                Task.due_date.isnot(None),
                Task.due_date < now,
                Task.status.notin_(_TERMINAL_TASK_STATUSES),
                Task.priority.in_(_HIGH_TASK_PRIORITIES),
            )
            .order_by(Task.due_date.asc())
            .limit(6)
        )
        for task_row in overdue_result.all():
            severity = "critical" if task_row.Task.priority == TaskPriority.CRITICAL else "high"
            items.append(
                {
                    "id": f"overdue-task-{task_row.Task.id}",
                    "alert_type": "overdue_task",
                    "severity": severity,
                    "title": task_row.Task.title,
                    "message": task_row.Task.description or "High-priority overdue task",
                    "entity_type": "task",
                    "entity_id": task_row.Task.id,
                    "case_id": task_row.Task.case_id,
                    "case_number": task_row.case_number,
                }
            )

        return {"total": len(items), "items": items}
