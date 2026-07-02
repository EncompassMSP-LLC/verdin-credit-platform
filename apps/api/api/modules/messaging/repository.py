"""Secure messaging repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.messaging.models import MessageThread, ThreadMessage


class MessagingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_thread_by_case(
        self,
        *,
        organization_id: uuid.UUID,
        case_id: uuid.UUID,
    ) -> MessageThread | None:
        result = await self._session.execute(
            select(MessageThread).where(
                MessageThread.organization_id == organization_id,
                MessageThread.case_id == case_id,
                MessageThread.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_thread_by_id(
        self,
        thread_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> MessageThread | None:
        result = await self._session.execute(
            select(MessageThread).where(
                MessageThread.id == thread_id,
                MessageThread.organization_id == organization_id,
                MessageThread.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_messages(
        self,
        thread_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> list[ThreadMessage]:
        result = await self._session.execute(
            select(ThreadMessage)
            .where(
                ThreadMessage.thread_id == thread_id,
                ThreadMessage.organization_id == organization_id,
            )
            .order_by(ThreadMessage.created_at.asc())
        )
        return list(result.scalars().all())

    async def create_thread(self, thread: MessageThread) -> MessageThread:
        self._session.add(thread)
        await self._session.flush()
        await self._session.refresh(thread)
        return thread

    async def create_message(self, message: ThreadMessage) -> ThreadMessage:
        self._session.add(message)
        await self._session.flush()
        await self._session.refresh(message)
        return message

    async def save_thread(self, thread: MessageThread) -> MessageThread:
        await self._session.flush()
        await self._session.refresh(thread)
        return thread
