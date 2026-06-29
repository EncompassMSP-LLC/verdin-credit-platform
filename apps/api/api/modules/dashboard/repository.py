"""Dashboard repository — aggregated read-only queries for the operations snapshot."""

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
from api.modules.tasks.models import Task, TaskStatus
from api.modules.timeline.models import TimelineEvent

_TERMINAL_TASK_STATUSES = (TaskStatus.COMPLETED, TaskStatus.CANCELED)
_OPEN_CASE_STATUSES = (CaseStatus.OPEN, CaseStatus.ACTIVE)
_CLOSED_CASE_STATUSES = (CaseStatus.RESOLVED, CaseStatus.CLOSED)
_HIGH_PRIORITIES = (CasePriority.HIGH, CasePriority.CRITICAL)
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
        start_of_week = start_of_day - timedelta(days=start_of_day.weekday())
        start_of_month = start_of_day.replace(day=1)

        kpis = await self._get_kpis(organization_id, now)
        processing = await self._get_processing(organization_id, start_of_day)
        work_queue = await self._get_work_queue(organization_id, now)
        timeline = await self._get_timeline(organization_id)
        ai = await self._get_ai_metrics(organization_id)
        performance = await self._get_performance(
            organization_id, start_of_week, start_of_month, now
        )

        return {
            "kpis": kpis,
            "processing": processing,
            "tasks": work_queue,
            "timeline": timeline,
            "ai": ai,
            "performance": performance,
        }

    async def _count(self, query: Any) -> int:
        result = await self._session.execute(select(func.count()).select_from(query.subquery()))
        return int(result.scalar_one())

    async def _get_kpis(self, organization_id: uuid.UUID, now: datetime) -> dict[str, Any]:
        open_cases_q = select(Case).where(
            Case.organization_id == organization_id,
            Case.deleted_at.is_(None),
            Case.status.in_(_OPEN_CASE_STATUSES),
        )
        active_accounts_q = select(Account).where(
            Account.organization_id == organization_id,
            Account.deleted_at.is_(None),
            Account.account_status == AccountStatus.OPEN,
        )
        pending_tasks_q = select(Task).where(
            Task.organization_id == organization_id,
            Task.deleted_at.is_(None),
            Task.status.notin_(_TERMINAL_TASK_STATUSES),
        )
        docs_processing_q = select(Document).where(
            Document.organization_id == organization_id,
            Document.deleted_at.is_(None),
            Document.processing_status.in_(_PROCESSING_ACTIVE),
        )
        ocr_queue_q = select(Document).where(
            Document.organization_id == organization_id,
            Document.deleted_at.is_(None),
            Document.processing_status.in_(_OCR_QUEUE_STATUSES),
        )

        avg_resolution = await self._session.execute(
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
        avg_seconds = avg_resolution.scalar_one()
        avg_hours = round(float(avg_seconds) / 3600, 1) if avg_seconds is not None else None

        return {
            "open_cases": await self._count(open_cases_q),
            "active_accounts": await self._count(active_accounts_q),
            "pending_tasks": await self._count(pending_tasks_q),
            "documents_processing": await self._count(docs_processing_q),
            "ocr_queue": await self._count(ocr_queue_q),
            "average_resolution_time_hours": avg_hours,
        }

    async def _get_processing(
        self, organization_id: uuid.UUID, start_of_day: datetime
    ) -> dict[str, int]:
        base_doc = and_(
            Document.organization_id == organization_id,
            Document.deleted_at.is_(None),
        )

        uploads_today_q = select(Document).where(base_doc, Document.created_at >= start_of_day)
        ocr_running_q = select(Document).where(
            base_doc,
            Document.processing_status == DocumentProcessingStatus.PROCESSING,
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
            "uploads_today": await self._count(uploads_today_q),
            "ocr_running": await self._count(ocr_running_q),
            "ocr_failed": await self._count(ocr_failed_q),
            "classification_pending": await self._count(classification_pending_q),
            "metadata_pending": await self._count(metadata_pending_q),
            "entity_resolution_pending": await self._count(entity_resolution_pending_q),
        }

    async def _get_work_queue(
        self, organization_id: uuid.UUID, now: datetime
    ) -> dict[str, list[dict[str, Any]]]:
        overdue_result = await self._session.execute(
            select(Task, Case.case_number)
            .outerjoin(Case, Case.id == Task.case_id)
            .where(
                Task.organization_id == organization_id,
                Task.deleted_at.is_(None),
                Task.due_date.isnot(None),
                Task.due_date < now,
                Task.status.notin_(_TERMINAL_TASK_STATUSES),
            )
            .order_by(Task.due_date.asc())
            .limit(8)
        )
        overdue_tasks = [
            {
                "id": row.Task.id,
                "title": row.Task.title,
                "subtitle": row.Task.description,
                "entity_type": "task",
                "priority": row.Task.priority.value,
                "due_date": row.Task.due_date,
                "case_id": row.Task.case_id,
                "case_number": row.case_number,
            }
            for row in overdue_result.all()
        ]

        cases_result = await self._session.execute(
            select(Case)
            .where(
                Case.organization_id == organization_id,
                Case.deleted_at.is_(None),
                Case.status.in_(_OPEN_CASE_STATUSES),
                Case.priority.in_(_HIGH_PRIORITIES),
            )
            .order_by(Case.priority.desc(), Case.opened_at.asc())
            .limit(8)
        )
        high_priority_cases = [
            {
                "id": case.id,
                "title": case.title,
                "subtitle": case.client_name,
                "entity_type": "case",
                "priority": case.priority.value,
                "due_date": None,
                "case_id": case.id,
                "case_number": case.case_number,
            }
            for case in cases_result.scalars().all()
        ]

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
            .limit(8)
        )
        documents_requiring_review = [
            {
                "id": row.Document.id,
                "title": row.Document.title,
                "subtitle": row.Document.file_name,
                "entity_type": "document",
                "priority": None,
                "due_date": None,
                "case_id": row.Document.case_id,
                "case_number": row.case_number,
            }
            for row in review_result.all()
        ]

        ocr_failed_result = await self._session.execute(
            select(Document, Case.case_number)
            .outerjoin(Case, Case.id == Document.case_id)
            .where(
                Document.organization_id == organization_id,
                Document.deleted_at.is_(None),
                Document.processing_status == DocumentProcessingStatus.FAILED,
            )
            .order_by(Document.updated_at.desc())
            .limit(8)
        )
        ocr_failures = [
            {
                "id": row.Document.id,
                "title": row.Document.title,
                "subtitle": row.Document.ocr_error or row.Document.file_name,
                "entity_type": "document",
                "priority": None,
                "due_date": None,
                "case_id": row.Document.case_id,
                "case_number": row.case_number,
            }
            for row in ocr_failed_result.all()
        ]

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
            .limit(8)
        )
        unresolved_entity_matches = [
            {
                "id": row.Document.id,
                "title": row.Document.title,
                "subtitle": row.Document.file_name,
                "entity_type": "document",
                "priority": None,
                "due_date": None,
                "case_id": row.Document.case_id,
                "case_number": row.case_number,
            }
            for row in unresolved_result.all()
        ]

        return {
            "overdue_tasks": overdue_tasks,
            "high_priority_cases": high_priority_cases,
            "documents_requiring_review": documents_requiring_review,
            "ocr_failures": ocr_failures,
            "unresolved_entity_matches": unresolved_entity_matches,
        }

    async def _get_timeline(self, organization_id: uuid.UUID) -> list[dict[str, Any]]:
        CaseAlias = aliased(Case)
        result = await self._session.execute(
            select(TimelineEvent, CaseAlias.case_number)
            .outerjoin(CaseAlias, CaseAlias.id == TimelineEvent.case_id)
            .where(TimelineEvent.organization_id == organization_id)
            .order_by(TimelineEvent.occurred_at.desc())
            .limit(12)
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
                "metadata": dict(row.TimelineEvent.event_metadata or {}),
            }
            for row in result.all()
        ]

    async def _get_ai_metrics(self, organization_id: uuid.UUID) -> dict[str, Any]:
        base_doc = and_(
            Document.organization_id == organization_id,
            Document.deleted_at.is_(None),
        )

        classified_q = select(Document).where(base_doc, Document.document_type.isnot(None))
        metadata_extracted_q = select(DocumentMetadata).where(
            DocumentMetadata.organization_id == organization_id,
            DocumentMetadata.metadata_status == MetadataStatus.EXTRACTED,
        )

        classified_count = await self._count(classified_q)
        metadata_count = await self._count(metadata_extracted_q)

        resolved_docs_q = (
            select(Document.id)
            .join(DocumentEntityResolution, DocumentEntityResolution.document_id == Document.id)
            .where(
                base_doc,
                DocumentEntityResolution.resolution_status.in_(_RESOLVED_ENTITY_STATUSES),
            )
            .distinct()
        )
        resolved_count = await self._count(resolved_docs_q)

        resolution_rate = (
            round((resolved_count / metadata_count) * 100, 1) if metadata_count > 0 else 0.0
        )

        avg_conf_result = await self._session.execute(
            select(func.avg(Document.confidence_score)).where(
                base_doc,
                Document.confidence_score.isnot(None),
            )
        )
        avg_conf = avg_conf_result.scalar_one()
        average_confidence = round(float(avg_conf), 3) if avg_conf is not None else None

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

        return {
            "documents_classified": classified_count,
            "metadata_extracted": metadata_count,
            "entity_resolution_rate": resolution_rate,
            "average_confidence": average_confidence,
            "ai_ready_documents": await self._count(ai_ready_q),
        }

    async def _get_performance(
        self,
        organization_id: uuid.UUID,
        start_of_week: datetime,
        start_of_month: datetime,
        now: datetime,
    ) -> dict[str, Any]:
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

        account_count_result = await self._session.execute(
            select(func.count()).where(
                Account.organization_id == organization_id,
                Account.deleted_at.is_(None),
            )
        )
        total_accounts = int(account_count_result.scalar_one() or 0)

        document_count_result = await self._session.execute(
            select(func.count()).where(
                Document.organization_id == organization_id,
                Document.deleted_at.is_(None),
            )
        )
        total_documents = int(document_count_result.scalar_one() or 0)

        cases_with_accounts_result = await self._session.execute(
            select(func.count(func.distinct(Account.case_id))).where(
                Account.organization_id == organization_id,
                Account.deleted_at.is_(None),
            )
        )
        cases_with_accounts = int(cases_with_accounts_result.scalar_one() or 0)

        cases_with_documents_result = await self._session.execute(
            select(func.count(func.distinct(Document.case_id))).where(
                Document.organization_id == organization_id,
                Document.deleted_at.is_(None),
                Document.case_id.isnot(None),
            )
        )
        cases_with_documents = int(cases_with_documents_result.scalar_one() or 0)

        opened_week_q = select(Case).where(
            Case.organization_id == organization_id,
            Case.deleted_at.is_(None),
            Case.opened_at >= start_of_week,
        )
        completed_month_q = select(Case).where(
            Case.organization_id == organization_id,
            Case.deleted_at.is_(None),
            Case.closed_at.isnot(None),
            Case.closed_at >= start_of_month,
            Case.status.in_(_CLOSED_CASE_STATUSES),
        )

        open_or_active = await self._count(
            select(Case).where(
                Case.organization_id == organization_id,
                Case.deleted_at.is_(None),
                Case.status.in_(_OPEN_CASE_STATUSES),
            )
        )
        closed_total = await self._count(
            select(Case).where(
                Case.organization_id == organization_id,
                Case.deleted_at.is_(None),
                Case.status.in_(_CLOSED_CASE_STATUSES),
            )
        )
        resolution_denominator = open_or_active + closed_total
        resolution_rate = (
            round((closed_total / resolution_denominator) * 100, 1)
            if resolution_denominator > 0
            else 0.0
        )

        throughput_q = select(Document).where(
            Document.organization_id == organization_id,
            Document.deleted_at.is_(None),
            Document.processing_status == DocumentProcessingStatus.COMPLETED,
            Document.updated_at >= start_of_day,
        )

        return {
            "average_accounts_per_case": round(total_accounts / cases_with_accounts, 1)
            if cases_with_accounts > 0
            else 0.0,
            "average_documents_per_case": round(total_documents / cases_with_documents, 1)
            if cases_with_documents > 0
            else 0.0,
            "cases_opened_this_week": await self._count(opened_week_q),
            "cases_completed_this_month": await self._count(completed_month_q),
            "resolution_rate": resolution_rate,
            "processing_throughput": await self._count(throughput_q),
        }
