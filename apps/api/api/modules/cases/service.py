"""Case management service — business logic for case CRUD."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.auth.repository import UserRepository
from api.modules.cases.models import Case, CaseStatus
from api.modules.cases.permissions import CASE_DELETE_ROLE, CASE_WRITE_ROLE
from api.modules.cases.repository import CaseListFilters, CaseRepository
from api.modules.cases.schemas import CaseCreate, CaseListParams, CaseResponse, CaseUpdate
from api.repositories.case import CaseRepositoryProtocol
from api.repositories.user import UserRepositoryProtocol


class CaseService:
    def __init__(
        self,
        case_repo: CaseRepositoryProtocol,
        user_repo: UserRepositoryProtocol | None = None,
    ) -> None:
        self._cases = case_repo
        self._users = user_repo

    @classmethod
    def from_session(cls, session: AsyncSession) -> "CaseService":
        return cls(CaseRepository(session), UserRepository(session))

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, CASE_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to modify cases",
            )

    def _require_delete(self, user: User) -> None:
        if not has_permission(user.role, CASE_DELETE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete cases",
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

    async def _get_case_for_user(self, case_id: uuid.UUID, user: User) -> Case:
        organization_id = self._require_organization(user)
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        return case

    @staticmethod
    def _apply_status_timestamps(case: Case, new_status: CaseStatus | None) -> None:
        if new_status is None:
            return
        if new_status in (CaseStatus.RESOLVED, CaseStatus.CLOSED) and case.closed_at is None:
            case.closed_at = datetime.now(UTC)
        if new_status in (CaseStatus.OPEN, CaseStatus.ACTIVE, CaseStatus.ON_HOLD):
            case.closed_at = None

    async def create_case(self, user: User, data: CaseCreate) -> CaseResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        await self._validate_assignee(data.assigned_user_id, organization_id)

        if data.case_number:
            existing = await self._cases.get_by_case_number(data.case_number)
            if existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Case number already exists",
                )

        opened_at = data.opened_at or datetime.now(UTC)
        closed_at = None
        if data.status in (CaseStatus.RESOLVED, CaseStatus.CLOSED):
            closed_at = datetime.now(UTC)

        case = Case(
            organization_id=organization_id,
            title=data.title,
            client_name=data.client_name,
            client_email=str(data.client_email) if data.client_email else None,
            case_number=data.case_number,
            status=data.status,
            stage=data.stage,
            priority=data.priority,
            assigned_to_id=data.assigned_user_id,
            summary=data.summary,
            notes=data.notes,
            opened_at=opened_at,
            closed_at=closed_at,
        )
        apply_audit_on_create(case, user.id)
        created = await self._cases.create(case)
        return CaseResponse.from_model(created)

    async def list_cases(
        self,
        user: User,
        params: CaseListParams,
    ) -> PaginatedResponse[CaseResponse]:
        organization_id = self._require_organization(user)
        filters = CaseListFilters(
            organization_id=organization_id,
            search=params.search,
            status=params.status,
            stage=params.stage,
            priority=params.priority,
            assigned_user_id=params.assigned_user_id,
            skip=params.offset,
            limit=params.limit,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
        )
        items, total = await self._cases.list_cases(filters)
        return paginate(
            [CaseResponse.from_model(item) for item in items],
            total,
            params.page,
            params.page_size,
        )

    async def get_case(self, user: User, case_id: uuid.UUID) -> CaseResponse:
        case = await self._get_case_for_user(case_id, user)
        return CaseResponse.from_model(case)

    async def update_case(
        self,
        user: User,
        case_id: uuid.UUID,
        data: CaseUpdate,
    ) -> CaseResponse:
        self._require_write(user)
        case = await self._get_case_for_user(case_id, user)
        organization_id = self._require_organization(user)

        updates = data.model_dump(exclude_unset=True)
        if "case_number" in updates and updates["case_number"]:
            existing = await self._cases.get_by_case_number(updates["case_number"])
            if existing is not None and existing.id != case.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Case number already exists",
                )

        if "assigned_user_id" in updates:
            await self._validate_assignee(updates["assigned_user_id"], organization_id)

        field_map = {
            "assigned_user_id": "assigned_to_id",
            "client_email": "client_email",
        }
        for key, value in updates.items():
            attr = field_map.get(key, key)
            if key == "client_email" and value is not None:
                value = str(value)
            setattr(case, attr, value)

        if "status" in updates:
            self._apply_status_timestamps(case, updates["status"])
        if "closed_at" in updates:
            case.closed_at = updates["closed_at"]

        apply_audit_on_update(case, user.id)
        updated = await self._cases.update(case)
        return CaseResponse.from_model(updated)

    async def delete_case(self, user: User, case_id: uuid.UUID) -> None:
        self._require_delete(user)
        case = await self._get_case_for_user(case_id, user)
        case.soft_delete()
        apply_audit_on_update(case, user.id)
        await self._cases.update(case)
