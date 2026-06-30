"""Task management endpoints."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse
from api.database.session import get_db
from api.modules.auth.dependencies import get_current_user
from api.modules.auth.models import User
from api.modules.tasks.models import TaskPriority, TaskStatus
from api.modules.tasks.schemas import (
    TaskCreate,
    TaskListParams,
    TaskResponse,
    TaskSortField,
    TaskSortOrder,
    TaskUpdate,
)
from api.modules.tasks.service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService.from_session(db)


def get_task_list_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    case_id: uuid.UUID | None = None,
    account_id: uuid.UUID | None = None,
    document_id: uuid.UUID | None = None,
    assigned_user_id: uuid.UUID | None = None,
    due_before: datetime | None = None,
    due_after: datetime | None = None,
    overdue: bool | None = None,
    sort_by: TaskSortField = "created_at",
    sort_order: TaskSortOrder = "desc",
) -> TaskListParams:
    return TaskListParams(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        priority=priority,
        case_id=case_id,
        account_id=account_id,
        document_id=document_id,
        assigned_user_id=assigned_user_id,
        due_before=due_before,
        due_after=due_after,
        overdue=overdue,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    return await service.create_task(current_user, body)


@router.get("", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
    params: TaskListParams = Depends(get_task_list_params),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> PaginatedResponse[TaskResponse]:
    return await service.list_tasks(current_user, params)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    return await service.get_task(current_user, task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    body: TaskUpdate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    return await service.update_task(current_user, task_id, body)


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    return await service.complete_task(current_user, task_id)


@router.post("/{task_id}/reopen", response_model=TaskResponse)
async def reopen_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    return await service.reopen_task(current_user, task_id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> None:
    await service.delete_task(current_user, task_id)
