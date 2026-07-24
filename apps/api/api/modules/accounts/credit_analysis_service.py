"""Staff credit-analysis runs + portal readiness read model (Vol 22 E3)."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.permissions import has_permission
from api.modules.accounts.credit_analysis import ADVISORY_DISCLAIMER, compose_credit_analysis
from api.modules.accounts.credit_analysis_export import (
    CreditAnalysisExportFormat,
    build_credit_analysis_export,
)
from api.modules.accounts.credit_analysis_run_models import CreditAnalysisRun
from api.modules.accounts.credit_analysis_run_repository import (
    CreditAnalysisRunListFilters,
    CreditAnalysisRunRepository,
)
from api.modules.accounts.credit_analysis_schemas import (
    CreditAnalysisRunListResponse,
    CreditAnalysisRunResponse,
    CreditAnalysisRunSummary,
    PortalCaseReadinessResponse,
    PortalReadinessAccount,
    PortalReadinessBlocker,
    PortalReadinessDimension,
)
from api.modules.accounts.permissions import ACCOUNT_WRITE_ROLE
from api.modules.accounts.repository import AccountRepository
from api.modules.auth.models import User
from api.modules.cases.models import Case
from api.modules.cases.repository import CaseRepository


class CreditAnalysisService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._runs = CreditAnalysisRunRepository(session)
        self._accounts = AccountRepository(session)
        self._cases = CaseRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> CreditAnalysisService:
        return cls(session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with an organization",
            )
        return user.organization_id

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, ACCOUNT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    async def _get_case(self, case_id: uuid.UUID, organization_id: uuid.UUID) -> Case:
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        return case

    def _to_summary(self, row: CreditAnalysisRun) -> CreditAnalysisRunSummary:
        return CreditAnalysisRunSummary(
            id=row.id,
            case_id=row.case_id,
            generated_at=row.generated_at,
            reports_evaluated=row.reports_evaluated,
            tradelines_evaluated=row.tradelines_evaluated,
            borrower_readiness_score=row.borrower_readiness_score,
            mortgage_readiness_score=row.mortgage_readiness_score,
            schema_version=row.schema_version,
            band=row.band,
            status=row.status,
        )

    def _to_response(self, row: CreditAnalysisRun) -> CreditAnalysisRunResponse:
        return CreditAnalysisRunResponse(
            **self._to_summary(row).model_dump(),
            payload=row.payload,
            formula_version=row.formula_version,
            score_version=row.score_version,
            inputs_hash=row.inputs_hash,
            published_at=row.published_at,
        )

    async def create_run(self, user: User, case_id: uuid.UUID) -> CreditAnalysisRunResponse:
        """Compose + persist a published run (staff enqueue is the publish gate in v1)."""
        self._require_write(user)
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)

        accounts, _total = await self._accounts.list_by_case(
            case_id,
            organization_id,
            skip=0,
            limit=500,
        )
        composed = compose_credit_analysis(list(accounts))
        row = await self._runs.create(
            organization_id=organization_id,
            case_id=case_id,
            generated_by_id=user.id,
            status="published",
            schema_version=composed.schema_version,
            score_version=composed.score_version,
            formula_version=composed.formula_version,
            inputs_hash=composed.inputs_hash,
            reports_evaluated=composed.reports_evaluated,
            tradelines_evaluated=composed.tradelines_evaluated,
            borrower_readiness_score=composed.borrower_readiness_score,
            mortgage_readiness_score=composed.mortgage_readiness_score,
            band=composed.band,
            payload=composed.payload,
            published_by_id=user.id,
        )
        await self._session.commit()
        return self._to_response(row)

    async def list_runs(
        self,
        user: User,
        case_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> CreditAnalysisRunListResponse:
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)
        rows, _total = await self._runs.list_for_case(
            CreditAnalysisRunListFilters(
                organization_id=organization_id,
                case_id=case_id,
                skip=skip,
                limit=limit,
            )
        )
        return CreditAnalysisRunListResponse(items=[self._to_summary(r) for r in rows])

    async def get_latest_run(self, user: User, case_id: uuid.UUID) -> CreditAnalysisRunResponse:
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)
        row = await self._runs.get_latest_for_case(
            organization_id=organization_id,
            case_id=case_id,
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No credit analysis run found for this case",
            )
        return self._to_response(row)

    async def get_run(
        self,
        user: User,
        case_id: uuid.UUID,
        run_id: uuid.UUID,
    ) -> CreditAnalysisRunResponse:
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)
        row = await self._runs.get_for_case(
            organization_id=organization_id,
            case_id=case_id,
            run_id=run_id,
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credit analysis run not found",
            )
        return self._to_response(row)

    async def export_run(
        self,
        user: User,
        case_id: uuid.UUID,
        run_id: uuid.UUID,
        *,
        export_format: CreditAnalysisExportFormat,
    ) -> tuple[bytes, str, str]:
        """Export a specific run as text or PDF. Operator-gated; no auto-transmit."""
        run_response = await self.get_run(user, case_id, run_id)
        return build_credit_analysis_export(run_response, export_format)

    async def get_portal_readiness(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> PortalCaseReadinessResponse:
        row = await self._runs.get_latest_for_case(
            organization_id=organization_id,
            case_id=case_id,
            status="published",
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Readiness not published yet",
            )
        payload = row.payload or {}
        dimensions = [PortalReadinessDimension(**d) for d in payload.get("dimensions", [])]
        blockers = [PortalReadinessBlocker(**b) for b in payload.get("blockers", [])]
        accounts = [PortalReadinessAccount(**a) for a in payload.get("accounts", [])]
        return PortalCaseReadinessResponse(
            case_id=row.case_id,
            overall=row.borrower_readiness_score,
            band=row.band,
            updated_at=row.published_at or row.generated_at,
            trend=payload.get("trend"),
            disclaimer=payload.get("disclaimer") or ADVISORY_DISCLAIMER,
            dimensions=dimensions,
            blockers=blockers,
            accounts=accounts,
        )
