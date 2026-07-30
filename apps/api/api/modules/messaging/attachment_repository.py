"""Repository for thread message attachments."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.messaging.attachment_models import ThreadMessageAttachment


class MessageAttachmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, attachment: ThreadMessageAttachment) -> ThreadMessageAttachment:
        self._session.add(attachment)
        await self._session.flush()
        await self._session.refresh(attachment)
        return attachment

    async def get_by_id(
        self,
        attachment_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID | None = None,
        case_id: uuid.UUID | None = None,
    ) -> ThreadMessageAttachment | None:
        query = select(ThreadMessageAttachment).where(
            ThreadMessageAttachment.id == attachment_id,
            ThreadMessageAttachment.organization_id == organization_id,
            ThreadMessageAttachment.deleted_at.is_(None),
        )
        if client_id is not None:
            query = query.where(ThreadMessageAttachment.client_id == client_id)
        if case_id is not None:
            query = query.where(ThreadMessageAttachment.case_id == case_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_messages(
        self,
        message_ids: list[uuid.UUID],
        *,
        organization_id: uuid.UUID,
    ) -> list[ThreadMessageAttachment]:
        if not message_ids:
            return []
        result = await self._session.execute(
            select(ThreadMessageAttachment)
            .where(
                ThreadMessageAttachment.organization_id == organization_id,
                ThreadMessageAttachment.message_id.in_(message_ids),
                ThreadMessageAttachment.deleted_at.is_(None),
            )
            .order_by(ThreadMessageAttachment.created_at.asc())
        )
        return list(result.scalars().all())

    async def list_by_ids(
        self,
        attachment_ids: list[uuid.UUID],
        *,
        organization_id: uuid.UUID,
        client_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> list[ThreadMessageAttachment]:
        if not attachment_ids:
            return []
        result = await self._session.execute(
            select(ThreadMessageAttachment).where(
                ThreadMessageAttachment.id.in_(attachment_ids),
                ThreadMessageAttachment.organization_id == organization_id,
                ThreadMessageAttachment.client_id == client_id,
                ThreadMessageAttachment.case_id == case_id,
                ThreadMessageAttachment.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def count_recent_uploads(
        self,
        *,
        organization_id: uuid.UUID,
        portal_user_id: uuid.UUID | None = None,
        staff_user_id: uuid.UUID | None = None,
        window: timedelta = timedelta(hours=1),
    ) -> int:
        since = datetime.now(UTC) - window
        query = (
            select(func.count())
            .select_from(ThreadMessageAttachment)
            .where(
                ThreadMessageAttachment.organization_id == organization_id,
                ThreadMessageAttachment.created_at >= since,
                ThreadMessageAttachment.deleted_at.is_(None),
            )
        )
        if portal_user_id is not None:
            query = query.where(
                ThreadMessageAttachment.uploaded_by_portal_user_id == portal_user_id
            )
        if staff_user_id is not None:
            query = query.where(ThreadMessageAttachment.uploaded_by_staff_user_id == staff_user_id)
        result = await self._session.execute(query)
        return int(result.scalar_one())

    async def soft_delete(self, attachment: ThreadMessageAttachment) -> ThreadMessageAttachment:
        attachment.deleted_at = datetime.now(UTC)
        await self._session.flush()
        await self._session.refresh(attachment)
        return attachment

    async def save(self, attachment: ThreadMessageAttachment) -> ThreadMessageAttachment:
        await self._session.flush()
        await self._session.refresh(attachment)
        return attachment
