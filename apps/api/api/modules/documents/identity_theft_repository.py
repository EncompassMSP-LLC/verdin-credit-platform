"""Repository for Identity Theft Case Center persistence."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.documents.identity_theft_models import (
    IdentityTheftAccountReview,
    IdentityTheftConfirmation,
    IdentityTheftIncident,
    IdentityTheftIncidentStatus,
    IdentityTheftIssueType,
    IdentityTheftProtection,
    IdentityTheftProtectionStatusValue,
    IdentityTheftProtectionType,
)


class IdentityTheftRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_open_incident_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> IdentityTheftIncident | None:
        result = await self._session.execute(
            select(IdentityTheftIncident)
            .where(
                IdentityTheftIncident.organization_id == organization_id,
                IdentityTheftIncident.case_id == case_id,
                IdentityTheftIncident.deleted_at.is_(None),
                IdentityTheftIncident.status != IdentityTheftIncidentStatus.CLOSED,
            )
            .order_by(IdentityTheftIncident.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_incident_for_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> IdentityTheftIncident | None:
        result = await self._session.execute(
            select(IdentityTheftIncident)
            .where(
                IdentityTheftIncident.organization_id == organization_id,
                IdentityTheftIncident.case_id == case_id,
                IdentityTheftIncident.deleted_at.is_(None),
            )
            .order_by(IdentityTheftIncident.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_incident(self, incident: IdentityTheftIncident) -> IdentityTheftIncident:
        self._session.add(incident)
        await self._session.flush()
        await self._session.refresh(incident)
        return incident

    async def list_account_reviews(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> list[IdentityTheftAccountReview]:
        result = await self._session.execute(
            select(IdentityTheftAccountReview)
            .where(
                IdentityTheftAccountReview.organization_id == organization_id,
                IdentityTheftAccountReview.case_id == case_id,
            )
            .order_by(IdentityTheftAccountReview.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_account_review(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        review_id: uuid.UUID,
    ) -> IdentityTheftAccountReview | None:
        result = await self._session.execute(
            select(IdentityTheftAccountReview).where(
                IdentityTheftAccountReview.organization_id == organization_id,
                IdentityTheftAccountReview.case_id == case_id,
                IdentityTheftAccountReview.id == review_id,
            )
        )
        return result.scalar_one_or_none()

    async def find_review_by_match(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        match_key: str | None,
        account_id: uuid.UUID | None,
        bureau: str | None,
        tradeline_index: int | None,
    ) -> IdentityTheftAccountReview | None:
        stmt = select(IdentityTheftAccountReview).where(
            IdentityTheftAccountReview.organization_id == organization_id,
            IdentityTheftAccountReview.case_id == case_id,
        )
        if account_id is not None:
            stmt = stmt.where(IdentityTheftAccountReview.account_id == account_id)
        elif match_key:
            stmt = stmt.where(IdentityTheftAccountReview.match_key == match_key)
        elif bureau is not None and tradeline_index is not None:
            stmt = stmt.where(
                IdentityTheftAccountReview.bureau == bureau,
                IdentityTheftAccountReview.tradeline_index == tradeline_index,
            )
        else:
            return None
        result = await self._session.execute(
            stmt.order_by(IdentityTheftAccountReview.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def add_account_review(
        self,
        review: IdentityTheftAccountReview,
    ) -> IdentityTheftAccountReview:
        self._session.add(review)
        await self._session.flush()
        await self._session.refresh(review)
        return review

    async def list_protections(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> list[IdentityTheftProtection]:
        result = await self._session.execute(
            select(IdentityTheftProtection)
            .where(
                IdentityTheftProtection.organization_id == organization_id,
                IdentityTheftProtection.case_id == case_id,
            )
            .order_by(IdentityTheftProtection.protection_type.asc())
        )
        return list(result.scalars().all())

    async def upsert_protection(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        protection_type: IdentityTheftProtectionType,
        status: IdentityTheftProtectionStatusValue,
        placed_at: date | None,
        expires_at: date | None,
        source: str,
        notes: str | None,
        user_id: uuid.UUID | None,
    ) -> IdentityTheftProtection:
        result = await self._session.execute(
            select(IdentityTheftProtection).where(
                IdentityTheftProtection.organization_id == organization_id,
                IdentityTheftProtection.case_id == case_id,
                IdentityTheftProtection.protection_type == protection_type,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            row = IdentityTheftProtection(
                id=uuid.uuid4(),
                organization_id=organization_id,
                case_id=case_id,
                protection_type=protection_type,
                status=status,
                placed_at=placed_at,
                expires_at=expires_at,
                source=source,
                notes=notes,
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            self._session.add(row)
            await self._session.flush()
            await self._session.refresh(row)
            return row
        existing.status = status
        existing.placed_at = placed_at
        existing.expires_at = expires_at
        existing.source = source
        existing.notes = notes
        existing.updated_by_id = user_id
        await self._session.flush()
        await self._session.refresh(existing)
        return existing

    async def account_has_identity_theft_lock(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
        account_id: uuid.UUID | None = None,
        match_key: str | None = None,
    ) -> bool:
        """True when a review locks ordinary disputes (indicator or confirmed theft)."""
        reviews = await self.list_account_reviews(
            organization_id=organization_id,
            case_id=case_id,
        )
        for review in reviews:
            if not review.ordinary_dispute_locked:
                continue
            if account_id is not None and review.account_id == account_id:
                return True
            if match_key and review.match_key == match_key:
                return True
            # Confirmed identity theft always locks that account review
            if (
                review.issue_type == IdentityTheftIssueType.CONFIRMED_IDENTITY_THEFT_CLAIM
                and account_id is not None
                and review.account_id == account_id
            ):
                return True
            if review.consumer_confirmation == IdentityTheftConfirmation.IDENTITY_THEFT and (
                (account_id is not None and review.account_id == account_id)
                or (match_key and review.match_key == match_key)
            ):
                return True
        return False
