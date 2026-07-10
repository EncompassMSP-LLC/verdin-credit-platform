"""Compliance-gated dispute filing prep service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.dispute_filing_prep import get_dispute_filing_prep_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.accounts.dispute_filing_prep_processor import (
    approve_dispute_filing_prep_run,
    resolve_bureau_target,
    submit_dispute_filing_prep_run,
)
from api.modules.accounts.dispute_filing_prep_repository import (
    DisputeFilingPrepRunListFilters,
    DisputeFilingPrepRunRepository,
)
from api.modules.accounts.dispute_filing_prep_schemas import (
    DisputeFilingPrepRequest,
    DisputeFilingPrepRunListParams,
    DisputeFilingPrepRunResponse,
    DisputeFilingPrepRunResultResponse,
    DisputeFilingPrepStatusResponse,
)
from api.modules.accounts.permissions import ACCOUNT_READ_ROLE, ACCOUNT_WRITE_ROLE
from api.modules.accounts.repository import AccountRepository
from api.modules.auth.models import User
from api.modules.cases.repository import CaseRepository
from api.modules.compliance.consent_gates import require_signed_consents
from api.modules.compliance.repository import ConsentRepository


class DisputeFilingPrepService:
    def __init__(
        self,
        run_repo: DisputeFilingPrepRunRepository,
        account_repo: AccountRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._accounts = account_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> DisputeFilingPrepService:
        return cls(
            DisputeFilingPrepRunRepository(session),
            AccountRepository(session),
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
                detail="Insufficient permissions to view dispute filing prep runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit dispute filing prep runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve dispute filing prep runs",
            )

    def _require_ready(self) -> None:
        prep_status = get_dispute_filing_prep_status()
        if not prep_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Dispute filing prep is not ready",
                    "blockers": list(prep_status.blockers),
                },
            )

    def get_status_response(self) -> DisputeFilingPrepStatusResponse:
        return DisputeFilingPrepStatusResponse.from_status(get_dispute_filing_prep_status())

    async def list_runs(
        self,
        user: User,
        params: DisputeFilingPrepRunListParams,
    ) -> PaginatedResponse[DisputeFilingPrepRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            DisputeFilingPrepRunListFilters(
                skip=skip,
                limit=params.page_size,
                account_id=params.account_id,
            ),
        )
        items = [DisputeFilingPrepRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_prep(
        self,
        user: User,
        account_id: uuid.UUID,
        body: DisputeFilingPrepRequest,
    ) -> DisputeFilingPrepRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        account = await self._accounts.get_by_id(account_id, organization_id=organization_id)
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        if self._session is not None:
            case_repo = CaseRepository(self._session)
            case = await case_repo.get_by_id(account.case_id, organization_id=organization_id)
            if case is not None and case.client_id is not None:
                await require_signed_consents(
                    ConsentRepository(self._session),
                    organization_id=organization_id,
                    client_id=case.client_id,
                )

        bureau_target = resolve_bureau_target(
            account,
            body.bureau_target.value if body.bureau_target is not None else None,
        )
        summary = await submit_dispute_filing_prep_run(
            session=self._session,
            organization_id=organization_id,
            account_id=account_id,
            bureau_target=bureau_target,
            prep_summary=body.prep_summary,
            requested_by_user_id=user.id,
        )
        await self._session.commit()
        return DisputeFilingPrepRunResultResponse(
            completed_at=summary.completed_at,
            run=DisputeFilingPrepRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> DisputeFilingPrepRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_dispute_filing_prep_run(
                session=self._session,
                organization_id=organization_id,
                run_id=run_id,
                approved_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT
                if "not pending approval" in detail
                else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return DisputeFilingPrepRunResultResponse(
            completed_at=summary.completed_at,
            run=DisputeFilingPrepRunResponse.from_model(summary.run),
        )
