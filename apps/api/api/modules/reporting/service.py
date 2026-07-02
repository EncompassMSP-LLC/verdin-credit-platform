"""Reporting service — org-scoped operational read models."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.enterprise_reporting import get_enterprise_reporting_status
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.reporting.permissions import REPORTING_READ_ROLE
from api.modules.reporting.repository import OperationsReportingRepository
from api.modules.reporting.schemas import (
    BureauPerformanceItem,
    BureauPerformanceReporting,
    BureauPerformanceReportingResponse,
    ClientReportingMetrics,
    EnterpriseReportingStatusResponse,
    NotificationReportingMetrics,
    OperationsReporting,
    OperationsReportingResponse,
    TeamMemberProductivity,
    TeamProductivityReporting,
    TeamProductivityReportingResponse,
)


class ReportingService:
    def __init__(self, repo: OperationsReportingRepository) -> None:
        self._reporting = repo

    @classmethod
    def from_session(cls, session: AsyncSession) -> "ReportingService":
        return cls(OperationsReportingRepository(session))

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, REPORTING_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view reporting",
            )

    async def get_operations_summary(self, user: User) -> OperationsReportingResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        raw = await self._reporting.get_operations_summary(organization_id)
        return OperationsReportingResponse(
            generated_at=datetime.now(UTC),
            operations=OperationsReporting(
                clients=ClientReportingMetrics(**raw["clients"]),
                dispute_accounts=raw["dispute_accounts"],
                dispute_letters=raw["dispute_letters"],
                notifications=NotificationReportingMetrics(**raw["notifications"]),
                portal_users=raw["portal_users"],
            ),
        )

    async def get_operations_metrics(self, user: User) -> OperationsReporting:
        """Return operations metrics without envelope (for dashboard embedding)."""
        response = await self.get_operations_summary(user)
        return response.operations

    async def get_enterprise_status(self, user: User) -> EnterpriseReportingStatusResponse:
        self._require_read(user)
        self._require_organization(user)
        return get_enterprise_reporting_status()

    async def get_bureau_performance(self, user: User) -> BureauPerformanceReportingResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        raw = await self._reporting.get_bureau_performance(organization_id)
        return BureauPerformanceReportingResponse(
            generated_at=datetime.now(UTC),
            bureau_performance=BureauPerformanceReporting(
                bureaus=[BureauPerformanceItem(**item) for item in raw["bureaus"]],
                total_accounts=raw["total_accounts"],
            ),
        )

    async def get_team_productivity(self, user: User) -> TeamProductivityReportingResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        raw = await self._reporting.get_team_productivity(organization_id)
        return TeamProductivityReportingResponse(
            generated_at=datetime.now(UTC),
            team_productivity=TeamProductivityReporting(
                members=[TeamMemberProductivity(**item) for item in raw["members"]],
                open_tasks_total=raw["open_tasks_total"],
                completed_tasks_30d_total=raw["completed_tasks_30d_total"],
                assigned_open_cases_total=raw["assigned_open_cases_total"],
                closed_cases_30d_total=raw["closed_cases_30d_total"],
            ),
        )
