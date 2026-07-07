"""Admin-gated OAuth marketplace publishing service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.oauth_marketplace_publishing import get_oauth_marketplace_publishing_status
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.org_admin.oauth_marketplace_publishing_processor import (
    approve_oauth_marketplace_publishing_run,
    submit_oauth_marketplace_publishing_run,
)
from api.modules.org_admin.oauth_marketplace_publishing_repository import (
    OAuthMarketplacePublishingRunListFilters,
    OAuthMarketplacePublishingRunRepository,
)
from api.modules.org_admin.oauth_marketplace_publishing_schemas import (
    OAuthMarketplacePublishingRunListParams,
    OAuthMarketplacePublishingRunResponse,
    OAuthMarketplacePublishingRunResultResponse,
    OAuthMarketplacePublishingStatusResponse,
    OAuthMarketplacePublishingSubmitRequest,
)
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE


class OAuthMarketplacePublishingService:
    def __init__(
        self,
        run_repo: OAuthMarketplacePublishingRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> OAuthMarketplacePublishingService:
        return cls(OAuthMarketplacePublishingRunRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view OAuth marketplace publishing runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit OAuth marketplace publishing runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve OAuth marketplace publishing runs",
            )

    def _require_ready(self) -> None:
        publishing_status = get_oauth_marketplace_publishing_status()
        if not publishing_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "OAuth marketplace publishing is not ready",
                    "blockers": list(publishing_status.blockers),
                },
            )

    def get_status_response(self) -> OAuthMarketplacePublishingStatusResponse:
        return OAuthMarketplacePublishingStatusResponse.from_status(
            get_oauth_marketplace_publishing_status()
        )

    async def list_runs(
        self,
        user: User,
        params: OAuthMarketplacePublishingRunListParams,
    ) -> PaginatedResponse[OAuthMarketplacePublishingRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            OAuthMarketplacePublishingRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [OAuthMarketplacePublishingRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_oauth_app(
        self,
        user: User,
        oauth_developer_app_id: uuid.UUID,
        body: OAuthMarketplacePublishingSubmitRequest,
    ) -> OAuthMarketplacePublishingRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_oauth_marketplace_publishing_run(
                session=self._session,
                organization_id=organization_id,
                oauth_developer_app_id=oauth_developer_app_id,
                publishing_summary=body.publishing_summary,
                marketplace_listing_slug=body.marketplace_listing_slug,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not approved" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return OAuthMarketplacePublishingRunResultResponse(
            completed_at=summary.completed_at,
            run=OAuthMarketplacePublishingRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> OAuthMarketplacePublishingRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_oauth_marketplace_publishing_run(
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
        return OAuthMarketplacePublishingRunResultResponse(
            completed_at=summary.completed_at,
            run=OAuthMarketplacePublishingRunResponse.from_model(summary.run),
        )
