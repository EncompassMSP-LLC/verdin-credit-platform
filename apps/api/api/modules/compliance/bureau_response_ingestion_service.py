"""Service for bureau response ingestion audit scaffold."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.accounts.permissions import ACCOUNT_READ_ROLE, ACCOUNT_WRITE_ROLE
from api.modules.accounts.repository import AccountRepository
from api.modules.auth.models import User
from api.modules.cases.repository import CaseRepository
from api.modules.compliance.bureau_response_ingestion_models import (
    BureauResponseIngestionRunStatus,
)
from api.modules.compliance.bureau_response_ingestion_repository import (
    LIVE_POLLING_DEFERRAL_REASON,
    BureauResponseIngestionRunListFilters,
    BureauResponseIngestionRunRepository,
)
from api.modules.compliance.bureau_response_ingestion_schemas import (
    BureauResponseIngestionRunListParams,
    BureauResponseIngestionRunResponse,
    BureauResponseIngestionRunResultResponse,
    BureauResponseIngestionStartRequest,
    BureauResponseIngestionStatusResponse,
)


class BureauResponseIngestionService:
    def __init__(
        self,
        run_repo: BureauResponseIngestionRunRepository,
        account_repo: AccountRepository,
        case_repo: CaseRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._accounts = account_repo
        self._cases = case_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> BureauResponseIngestionService:
        return cls(
            BureauResponseIngestionRunRepository(session),
            AccountRepository(session),
            CaseRepository(session),
            session=session,
        )

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view bureau response ingestion runs",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to start bureau response ingestion runs",
            )

    def get_status_response(self) -> BureauResponseIngestionStatusResponse:
        return BureauResponseIngestionStatusResponse()

    async def list_runs(
        self,
        user: User,
        params: BureauResponseIngestionRunListParams,
    ) -> PaginatedResponse[BureauResponseIngestionRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            BureauResponseIngestionRunListFilters(
                skip=skip,
                limit=params.page_size,
                case_id=params.case_id,
                account_id=params.account_id,
            ),
        )
        items = [BureauResponseIngestionRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def get_run(self, user: User, run_id: uuid.UUID) -> BureauResponseIngestionRunResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        run = await self._runs.get_run_by_id(run_id)
        if run is None or run.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bureau response ingestion run not found",
            )
        return BureauResponseIngestionRunResponse.from_model(run)

    async def start_run(
        self,
        user: User,
        body: BureauResponseIngestionStartRequest,
    ) -> BureauResponseIngestionRunResultResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)

        if body.case_id is not None:
            case = await self._cases.get_by_id(body.case_id, organization_id=organization_id)
            if case is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        if body.account_id is not None:
            account = await self._accounts.get_by_id(
                body.account_id, organization_id=organization_id
            )
            if account is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
                )
            if body.case_id is not None and account.case_id != body.case_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Account does not belong to the specified case",
                )

        requested_at = self._runs.utcnow()
        run = await self._runs.create_run(
            organization_id=organization_id,
            case_id=body.case_id,
            account_id=body.account_id,
            bureau_target=body.bureau_target,
            status=BureauResponseIngestionRunStatus.DEFERRED,
            summary=body.summary,
            deferral_reason=LIVE_POLLING_DEFERRAL_REASON,
            requested_by_user_id=user.id,
            requested_at=requested_at,
        )
        if self._session is not None:
            await self._session.commit()
        return BureauResponseIngestionRunResultResponse(
            completed_at=requested_at,
            run=BureauResponseIngestionRunResponse.from_model(run),
        )
