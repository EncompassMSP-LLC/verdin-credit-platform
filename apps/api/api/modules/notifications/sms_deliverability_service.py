"""SMS deliverability dashboard service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.permissions import has_permission
from api.core.sms_deliverability_dashboard import (
    build_sms_deliverability_metrics,
    get_sms_deliverability_dashboard_status,
)
from api.modules.auth.models import User
from api.modules.notifications.models import SmsDeliveryLogStatus
from api.modules.notifications.permissions import NOTIFICATION_READ_ROLE
from api.modules.notifications.sms_campaign_models import SmsMarketingCampaignStatus
from api.modules.notifications.sms_deliverability_repository import SmsDeliverabilityRepository
from api.modules.notifications.sms_deliverability_schemas import (
    SmsDeliverabilityCampaignOutcome,
    SmsDeliverabilityDashboardStatusResponse,
    SmsDeliverabilityMetricsResponse,
)


class SmsDeliverabilityDashboardService:
    def __init__(
        self,
        repo: SmsDeliverabilityRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._repo = repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> SmsDeliverabilityDashboardService:
        return cls(SmsDeliverabilityRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, NOTIFICATION_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view SMS deliverability metrics",
            )

    def get_status_response(self) -> SmsDeliverabilityDashboardStatusResponse:
        return SmsDeliverabilityDashboardStatusResponse.from_status(
            get_sms_deliverability_dashboard_status()
        )

    async def get_metrics(self, user: User) -> SmsDeliverabilityMetricsResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        dashboard_status = get_sms_deliverability_dashboard_status()
        if not dashboard_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "SMS deliverability dashboard is not ready",
                    "blockers": list(dashboard_status.blockers),
                },
            )

        total_campaign_runs = await self._repo.count_campaign_runs(organization_id)
        completed_campaign_runs = await self._repo.count_campaign_runs_by_status(
            organization_id,
            SmsMarketingCampaignStatus.COMPLETED,
        )
        failed_campaign_runs = await self._repo.count_campaign_runs_by_status(
            organization_id,
            SmsMarketingCampaignStatus.FAILED,
        )
        pending_campaign_runs = await self._repo.count_campaign_runs_by_status(
            organization_id,
            SmsMarketingCampaignStatus.PENDING,
        )
        delivery_logs_sent = await self._repo.count_delivery_logs_by_status(
            organization_id,
            SmsDeliveryLogStatus.SENT,
        )
        delivery_logs_failed = await self._repo.count_delivery_logs_by_status(
            organization_id,
            SmsDeliveryLogStatus.FAILED,
        )
        recent_runs = await self._repo.list_recent_campaign_outcomes(organization_id)
        recent_outcomes = [SmsDeliverabilityCampaignOutcome.from_model(run) for run in recent_runs]

        raw = build_sms_deliverability_metrics(
            total_campaign_runs=total_campaign_runs,
            completed_campaign_runs=completed_campaign_runs,
            failed_campaign_runs=failed_campaign_runs,
            pending_campaign_runs=pending_campaign_runs,
            delivery_logs_sent=delivery_logs_sent,
            delivery_logs_failed=delivery_logs_failed,
            recent_campaign_outcomes=[item.model_dump() for item in recent_outcomes],
        )
        return SmsDeliverabilityMetricsResponse(
            total_campaign_runs=raw["total_campaign_runs"],
            completed_campaign_runs=raw["completed_campaign_runs"],
            failed_campaign_runs=raw["failed_campaign_runs"],
            pending_campaign_runs=raw["pending_campaign_runs"],
            delivery_logs_sent=raw["delivery_logs_sent"],
            delivery_logs_failed=raw["delivery_logs_failed"],
            delivery_success_rate=raw["delivery_success_rate"],
            recent_campaign_outcomes=recent_outcomes,
        )
