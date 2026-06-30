"""Task management service — business logic for task CRUD."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from verdin_event_bus import PlatformEvent

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.events import publish_platform_event
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.accounts.repository import AccountRepository
from api.modules.auth.models import User
from api.modules.auth.repository import UserRepository
from api.modules.cases.repository import CaseRepository
from api.modules.documents.repository import DocumentRepository
from api.modules.tasks.models import Task, TaskStatus
from api.modules.tasks.permissions import TASK_DELETE_ROLE, TASK_WRITE_ROLE
from api.modules.tasks.repository import TaskListFilters, TaskRepository
from api.modules.tasks.schemas import (
    TaskCreate,
    TaskListParams,
    TaskResponse,
    TaskUpdate,
)
from api.modules.timeline.builders import (
    task_completed_event,
    task_created_event,
    task_deleted_event,
    task_reopened_event,
    task_updated_event,
)


class TaskService:
    def __init__(
        self,
        task_repo: TaskRepository,
        case_repo: CaseRepository | None = None,
        account_repo: AccountRepository | None = None,
        document_repo: DocumentRepository | None = None,
        user_repo: UserRepository | None = None,
        session: AsyncSession | None = None,
    ) -> None:
        self._tasks = task_repo
        self._cases = case_repo
        self._accounts = account_repo
        self._documents = document_repo
        self._users = user_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> "TaskService":
        return cls(
            TaskRepository(session),
            CaseRepository(session),
            AccountRepository(session),
            DocumentRepository(session),
            UserRepository(session),
            session=session,
        )

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, TASK_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to modify tasks",
            )

    def _require_delete(self, user: User) -> None:
        if not has_permission(user.role, TASK_DELETE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete tasks",
            )

    async def _validate_assignee(
        self,
        assignee_id: uuid.UUID | None,
        organization_id: uuid.UUID,
    ) -> None:
        if assignee_id is None or self._users is None:
            return
        assignee = await self._users.get_by_id(assignee_id)
        if assignee is None or assignee.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Assigned user must belong to the same organization",
            )

    async def _validate_links(
        self,
        organization_id: uuid.UUID,
        *,
        case_id: uuid.UUID | None,
        account_id: uuid.UUID | None,
        document_id: uuid.UUID | None,
    ) -> None:
        if case_id is not None:
            if self._cases is None:
                return
            case = await self._cases.get_by_id(case_id, organization_id=organization_id)
            if case is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Case not found in organization",
                )
        if account_id is not None:
            if self._accounts is None:
                return
            account = await self._accounts.get_by_id(account_id, organization_id=organization_id)
            if account is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Account not found in organization",
                )
        if document_id is not None:
            if self._documents is None:
                return
            document = await self._documents.get_by_id(document_id, organization_id=organization_id)
            if document is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Document not found in organization",
                )

    async def _get_task_for_user(self, task_id: uuid.UUID, user: User) -> Task:
        organization_id = self._require_organization(user)
        task = await self._tasks.get_by_id(task_id, organization_id=organization_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task

    @staticmethod
    def _apply_completion_fields(
        task: Task,
        *,
        status: TaskStatus | None,
        performed_by: uuid.UUID,
    ) -> None:
        if status is None:
            return
        if status == TaskStatus.COMPLETED:
            if task.completed_at is None:
                task.completed_at = datetime.now(UTC)
            task.completed_by_id = performed_by
        elif status in (TaskStatus.OPEN, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED):
            task.completed_at = None
            task.completed_by_id = None

    async def _publish(self, event: PlatformEvent) -> None:
        if self._session is not None:
            await publish_platform_event(self._session, event)

    async def create_task(self, user: User, data: TaskCreate) -> TaskResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        await self._validate_assignee(data.assigned_user_id, organization_id)
        await self._validate_links(
            organization_id,
            case_id=data.case_id,
            account_id=data.account_id,
            document_id=data.document_id,
        )

        task = Task(
            organization_id=organization_id,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            due_date=data.due_date,
            case_id=data.case_id,
            account_id=data.account_id,
            document_id=data.document_id,
            assigned_user_id=data.assigned_user_id,
            source_module=data.source_module,
            source_event_id=data.source_event_id,
        )
        self._apply_completion_fields(task, status=data.status, performed_by=user.id)
        apply_audit_on_create(task, user.id)
        await self._tasks.create(task)
        await self._publish(task_created_event(task, user.id))
        return TaskResponse.from_model(task)

    async def list_tasks(
        self, user: User, params: TaskListParams
    ) -> PaginatedResponse[TaskResponse]:
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        filters = TaskListFilters(
            organization_id=organization_id,
            search=params.search,
            status=params.status,
            priority=params.priority,
            case_id=params.case_id,
            account_id=params.account_id,
            document_id=params.document_id,
            assigned_user_id=params.assigned_user_id,
            due_before=params.due_before,
            due_after=params.due_after,
            overdue=params.overdue,
            skip=skip,
            limit=params.page_size,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
        )
        items, total = await self._tasks.list_tasks(filters)
        return paginate(
            [TaskResponse.from_model(task) for task in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_task(self, user: User, task_id: uuid.UUID) -> TaskResponse:
        task = await self._get_task_for_user(task_id, user)
        return TaskResponse.from_model(task)

    async def update_task(
        self,
        user: User,
        task_id: uuid.UUID,
        data: TaskUpdate,
    ) -> TaskResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        task = await self._get_task_for_user(task_id, user)

        updates = data.model_dump(exclude_unset=True)
        if "assigned_user_id" in updates:
            await self._validate_assignee(updates["assigned_user_id"], organization_id)
        await self._validate_links(
            organization_id,
            case_id=updates.get("case_id", task.case_id),
            account_id=updates.get("account_id", task.account_id),
            document_id=updates.get("document_id", task.document_id),
        )

        for field, value in updates.items():
            setattr(task, field, value)

        if "status" in updates:
            self._apply_completion_fields(task, status=updates["status"], performed_by=user.id)

        apply_audit_on_update(task, user.id)
        await self._tasks.update(task)
        await self._publish(task_updated_event(task, user.id))
        return TaskResponse.from_model(task)

    async def complete_task(self, user: User, task_id: uuid.UUID) -> TaskResponse:
        self._require_write(user)
        task = await self._get_task_for_user(task_id, user)
        if task.status == TaskStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task is already completed",
            )
        if task.status == TaskStatus.CANCELED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Canceled tasks cannot be completed",
            )

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(UTC)
        task.completed_by_id = user.id
        apply_audit_on_update(task, user.id)
        await self._tasks.update(task)
        await self._publish(task_completed_event(task, user.id))
        return TaskResponse.from_model(task)

    async def reopen_task(self, user: User, task_id: uuid.UUID) -> TaskResponse:
        self._require_write(user)
        task = await self._get_task_for_user(task_id, user)
        if task.status not in (TaskStatus.COMPLETED, TaskStatus.CANCELED):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only completed or canceled tasks can be reopened",
            )

        task.status = TaskStatus.OPEN
        task.completed_at = None
        task.completed_by_id = None
        apply_audit_on_update(task, user.id)
        await self._tasks.update(task)
        await self._publish(task_reopened_event(task, user.id))
        return TaskResponse.from_model(task)

    async def delete_task(self, user: User, task_id: uuid.UUID) -> None:
        self._require_delete(user)
        task = await self._get_task_for_user(task_id, user)
        task.deleted_at = datetime.now(UTC)
        apply_audit_on_update(task, user.id)
        await self._tasks.update(task)
        await self._publish(task_deleted_event(task, user.id))
