"""Dashboard aggregation service — single snapshot for the operations command center."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.dashboard.permissions import DASHBOARD_READ_ROLE
from api.modules.dashboard.repository import DashboardRepository
from api.modules.dashboard.schemas import (
    DashboardAi,
    DashboardKpis,
    DashboardPerformance,
    DashboardProcessing,
    DashboardQueueItem,
    DashboardResponse,
    DashboardTimelineItem,
    DashboardWorkQueue,
)

# Polling interval hint for clients; future WebSocket push can reuse the same payload.
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
            kpis=DashboardKpis(**raw["kpis"]),
            processing=DashboardProcessing(**raw["processing"]),
            tasks=DashboardWorkQueue(
                overdue_tasks=[
                    DashboardQueueItem(**item) for item in raw["tasks"]["overdue_tasks"]
                ],
                high_priority_cases=[
                    DashboardQueueItem(**item) for item in raw["tasks"]["high_priority_cases"]
                ],
                documents_requiring_review=[
                    DashboardQueueItem(**item)
                    for item in raw["tasks"]["documents_requiring_review"]
                ],
                ocr_failures=[DashboardQueueItem(**item) for item in raw["tasks"]["ocr_failures"]],
                unresolved_entity_matches=[
                    DashboardQueueItem(**item) for item in raw["tasks"]["unresolved_entity_matches"]
                ],
            ),
            timeline=[DashboardTimelineItem(**item) for item in raw["timeline"]],
            ai=DashboardAi(**raw["ai"]),
            performance=DashboardPerformance(**raw["performance"]),
        )
