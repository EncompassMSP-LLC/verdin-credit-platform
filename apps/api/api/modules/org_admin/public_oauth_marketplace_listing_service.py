"""Admin-gated public OAuth marketplace listing service."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import UserRole
from api.core.pagination import PaginatedResponse, paginate
from api.core.permissions import has_permission
from api.core.public_oauth_marketplace_listings import get_public_oauth_marketplace_listing_status
from api.modules.auth.models import User
from api.modules.org_admin.permissions import ORG_ADMIN_READ_ROLE, ORG_ADMIN_WRITE_ROLE
from api.modules.org_admin.public_oauth_marketplace_listing_processor import (
    approve_public_oauth_marketplace_listing_run,
    submit_public_oauth_marketplace_listing_run,
)
from api.modules.org_admin.public_oauth_marketplace_listing_repository import (
    PublicOAuthMarketplaceListingRunListFilters,
    PublicOAuthMarketplaceListingRunRepository,
)
from api.modules.org_admin.public_oauth_marketplace_listing_schemas import (
    PublicOAuthMarketplaceListingRunListParams,
    PublicOAuthMarketplaceListingRunResponse,
    PublicOAuthMarketplaceListingRunResultResponse,
    PublicOAuthMarketplaceListingStatusResponse,
    PublicOAuthMarketplaceListingSubmitRequest,
)


class PublicOAuthMarketplaceListingService:
    def __init__(
        self,
        run_repo: PublicOAuthMarketplaceListingRunRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._runs = run_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> PublicOAuthMarketplaceListingService:
        return cls(PublicOAuthMarketplaceListingRunRepository(session), session=session)

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
                detail="Insufficient permissions to view public OAuth marketplace listing runs",
            )

    def _require_submit(self, user: User) -> None:
        if not has_permission(user.role, ORG_ADMIN_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to submit public OAuth marketplace listing runs",
            )

    def _require_approve(self, user: User) -> None:
        if user.role != UserRole.ADMIN and user.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to approve public OAuth marketplace listing runs",
            )

    def _require_ready(self) -> None:
        listing_status = get_public_oauth_marketplace_listing_status()
        if not listing_status.ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": "Public OAuth marketplace listings are not ready",
                    "blockers": list(listing_status.blockers),
                },
            )

    def get_status_response(self) -> PublicOAuthMarketplaceListingStatusResponse:
        return PublicOAuthMarketplaceListingStatusResponse.from_status(
            get_public_oauth_marketplace_listing_status()
        )

    async def list_runs(
        self,
        user: User,
        params: PublicOAuthMarketplaceListingRunListParams,
    ) -> PaginatedResponse[PublicOAuthMarketplaceListingRunResponse]:
        self._require_read(user)
        organization_id = self._require_organization(user)
        skip = (params.page - 1) * params.page_size
        runs, total = await self._runs.list_runs(
            organization_id,
            PublicOAuthMarketplaceListingRunListFilters(skip=skip, limit=params.page_size),
        )
        items = [PublicOAuthMarketplaceListingRunResponse.from_model(run) for run in runs]
        return paginate(items, total=total, page=params.page, page_size=params.page_size)

    async def submit_from_publishing_run(
        self,
        user: User,
        oauth_marketplace_publishing_run_id: uuid.UUID,
        body: PublicOAuthMarketplaceListingSubmitRequest,
    ) -> PublicOAuthMarketplaceListingRunResultResponse:
        self._require_submit(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await submit_public_oauth_marketplace_listing_run(
                session=self._session,
                organization_id=organization_id,
                oauth_marketplace_publishing_run_id=oauth_marketplace_publishing_run_id,
                listing_summary=body.listing_summary,
                public_listing_url=body.public_listing_url,
                requested_by_user_id=user.id,
            )
        except ValueError as exc:
            detail = str(exc)
            status_code = (
                status.HTTP_409_CONFLICT if "not approved" in detail else status.HTTP_404_NOT_FOUND
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        await self._session.commit()
        return PublicOAuthMarketplaceListingRunResultResponse(
            completed_at=summary.completed_at,
            run=PublicOAuthMarketplaceListingRunResponse.from_model(summary.run),
        )

    async def approve_run(
        self,
        user: User,
        run_id: uuid.UUID,
    ) -> PublicOAuthMarketplaceListingRunResultResponse:
        self._require_approve(user)
        self._require_ready()
        organization_id = self._require_organization(user)
        if self._session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session unavailable",
            )

        try:
            summary = await approve_public_oauth_marketplace_listing_run(
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
        return PublicOAuthMarketplaceListingRunResultResponse(
            completed_at=summary.completed_at,
            run=PublicOAuthMarketplaceListingRunResponse.from_model(summary.run),
        )
