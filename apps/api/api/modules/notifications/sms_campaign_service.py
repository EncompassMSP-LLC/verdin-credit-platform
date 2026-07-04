"""SMS marketing campaign service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.core.sms_marketing import get_sms_marketing_campaign_status
from api.modules.auth.models import User
from api.modules.notifications.permissions import NOTIFICATION_CREATE_ROLE
from api.modules.notifications.sms_campaign_processor import enqueue_sms_marketing_campaign
from api.modules.notifications.sms_campaign_repository import (
    SmsMarketingCampaignRunListFilters,
    SmsMarketingCampaignRunRepository,
)
from api.modules.notifications.sms_campaign_schemas import (
    SmsMarketingCampaignRunListParams,
    SmsMarketingCampaignRunRequest,
    SmsMarketingCampaignRunResponse,
    SmsMarketingCampaignRunResultResponse,
    SmsMarketingCampaignStatusResponse,
)


class SmsMarketingCampaignService:
    def __init__(
        self,
        run_repo: SmsMarketingCampaignRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> SmsMarketingCampaignService:
        return cls(SmsMarketingCampaignRunRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_create(self, user: User) -> None:
        if not has_permission(user.role, NOTIFICATION_CREATE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage SMS marketing campaigns",
            )

    def get_status_response(self) -> SmsMarketingCampaignStatusResponse:
        return SmsMarketingCampaignStatusResponse.from_status(get_sms_marketing_campaign_status())

    async def list_runs(
        self,
        user: User,
        params: SmsMarketingCampaignRunListParams,
    ) -> PaginatedResponse[SmsMarketingCampaignRunResponse]:
        self._require_create(user)
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            SmsMarketingCampaignRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [SmsMarketingCampaignRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def enqueue_campaign(
        self,
        user: User,
        body: SmsMarketingCampaignRunRequest,
    ) -> SmsMarketingCampaignRunResultResponse:
        self._require_create(user)
        organization_id = self._require_organization(user)
        campaign_status = get_sms_marketing_campaign_status()
        if not campaign_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "SMS marketing campaigns are not ready",
                    "blockers": list(campaign_status.blockers),
                },
            )
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        summary = await enqueue_sms_marketing_campaign(
            session=self._session,
            organization_id=organization_id,
            campaign_name=body.campaign_name,
            message_body=body.message_body,
            recipient_user_ids=body.recipient_user_ids,
            performed_by_user_id=user.id,
        )
        await self._session.commit()
        return SmsMarketingCampaignRunResultResponse(
            completed_at=summary.completed_at,
            run=SmsMarketingCampaignRunResponse.from_model(summary.run),
        )
