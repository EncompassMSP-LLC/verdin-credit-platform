"""Task repository — owns all Task database access."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from api.modules.tasks.models import Task, TaskPriority, TaskStatus
from api.modules.tasks.schemas import TaskSortField, TaskSortOrder

_TERMINAL_STATUSES = (TaskStatus.COMPLETED, TaskStatus.CANCELED)


@dataclass(frozen=True, slots=True)
class TaskListFilters:
    organization_id: uuid.UUID
    search: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    assigned_user_id: uuid.UUID | None = None
    due_before: datetime | None = None
    due_after: datetime | None = None
    overdue: bool | None = None
    skip: int = 0
    limit: int = 20
    sort_by: TaskSortField = "created_at"
    sort_order: TaskSortOrder = "desc"


_SORT_COLUMNS: dict[TaskSortField, InstrumentedAttribute[Any]] = {
    "created_at": Task.created_at,
    "updated_at": Task.updated_at,
    "title": Task.title,
    "status": Task.status,
    "priority": Task.priority,
    "due_date": Task.due_date,
}


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(
        self,
        task_id: str | uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
    ) -> Task | None:
        uid = uuid.UUID(str(task_id))
        query = select(Task).where(Task.id == uid, Task.deleted_at.is_(None))
        if organization_id is not None:
            query = query.where(Task.organization_id == organization_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_tasks(self, filters: TaskListFilters) -> tuple[list[Task], int]:
        base = select(Task).where(
            Task.organization_id == filters.organization_id,
            Task.deleted_at.is_(None),
        )

        if filters.status is not None:
            base = base.where(Task.status == filters.status)
        if filters.priority is not None:
            base = base.where(Task.priority == filters.priority)
        if filters.case_id is not None:
            base = base.where(Task.case_id == filters.case_id)
        if filters.account_id is not None:
            base = base.where(Task.account_id == filters.account_id)
        if filters.document_id is not None:
            base = base.where(Task.document_id == filters.document_id)
        if filters.assigned_user_id is not None:
            base = base.where(Task.assigned_user_id == filters.assigned_user_id)
        if filters.due_before is not None:
            base = base.where(Task.due_date.isnot(None), Task.due_date <= filters.due_before)
        if filters.due_after is not None:
            base = base.where(Task.due_date.isnot(None), Task.due_date >= filters.due_after)
        if filters.overdue:
            now = datetime.now(UTC)
            base = base.where(
                Task.due_date.isnot(None),
                Task.due_date < now,
                Task.status.notin_(_TERMINAL_STATUSES),
            )
        if filters.search:
            term = f"%{filters.search.strip()}%"
            base = base.where(
                or_(
                    Task.title.ilike(term),
                    Task.description.ilike(term),
                )
            )

        count_query = select(func.count()).select_from(base.subquery())
        total = int((await self._session.execute(count_query)).scalar_one())

        sort_column = _SORT_COLUMNS[filters.sort_by]
        order = sort_column.asc() if filters.sort_order == "asc" else sort_column.desc()

        result = await self._session.execute(
            base.order_by(order).offset(filters.skip).limit(filters.limit)
        )
        return list(result.scalars().all()), total

    async def create(self, task: Task) -> Task:
        self._session.add(task)
        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def update(self, task: Task) -> Task:
        await self._session.flush()
        await self._session.refresh(task)
        return task
