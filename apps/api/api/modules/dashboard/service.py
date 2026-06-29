"""Dashboard aggregation service — Mission Control snapshot."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.dashboard.permissions import DASHBOARD_READ_ROLE
from api.modules.dashboard.repository import DashboardRepository
from api.modules.dashboard.schemas import (
    DashboardAccounts,
    DashboardAlertItem,
    DashboardAlerts,
    DashboardCases,
    DashboardDocuments,
    DashboardOverview,
    DashboardPerformance,
    DashboardProcessing,
    DashboardResponse,
    DashboardTasks,
    DashboardTimelineItem,
)

DASHBOARD_REFRESH_SECONDS = 30


class DashboardService:
    def __init__(self, repo: DashboardRepository) -> None:
        self._dashboard = repo

    @classmethod
    def from_session(cls, session: AsyncSession) -> "DashboardService":
        return cls(DashboardRepository(session))

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, DASHBOARD_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view dashboard",
            )

    async def get_snapshot(self, user: User) -> DashboardResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        raw = await self._dashboard.get_snapshot(organization_id)

        return DashboardResponse(
            generated_at=datetime.now(UTC),
            refresh_seconds=DASHBOARD_REFRESH_SECONDS,
            overview=DashboardOverview(**raw["overview"]),
            cases=DashboardCases(**raw["cases"]),
            accounts=DashboardAccounts(**raw["accounts"]),
            documents=DashboardDocuments(**raw["documents"]),
            timeline=[DashboardTimelineItem(**item) for item in raw["timeline"]],
            tasks=DashboardTasks(**raw["tasks"]),
            processing=DashboardProcessing(**raw["processing"]),
            performance=DashboardPerformance(**raw["performance"]),
            alerts=DashboardAlerts(
                total=raw["alerts"]["total"],
                items=[DashboardAlertItem(**item) for item in raw["alerts"]["items"]],
            ),
        )
