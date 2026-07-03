"""Secure messaging service — case-scoped threads for portal and staff."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.audit import apply_audit_on_create, apply_audit_on_update
from api.core.events import publish_platform_event
from api.core.messaging import get_messaging_center_status
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.cases.models import Case
from api.modules.cases.repository import CaseRepository
from api.modules.client_portal.models import ClientPortalUser
from api.modules.client_portal.push_dispatcher import dispatch_staff_message_push
from api.modules.messaging.models import (
    MessageSenderRole,
    MessageThread,
    MessageThreadStatus,
    ThreadMessage,
)
from api.modules.messaging.permissions import MESSAGE_READ_ROLE, MESSAGE_WRITE_ROLE
from api.modules.messaging.repository import MessagingRepository
from api.modules.messaging.schemas import (
    CaseMessageThreadResponse,
    MessageCreate,
    MessagingCenterStatusResponse,
    ThreadMessageResponse,
)
from api.modules.timeline.builders import portal_message_sent_event, staff_message_sent_event


class MessagingService:
    def __init__(
        self,
        messaging_repo: MessagingRepository,
        case_repo: CaseRepository,
        session: AsyncSession | None = None,
    ) -> None:
        self._messaging = messaging_repo
        self._cases = case_repo
        self._session = session

    @classmethod
    def from_session(cls, session: AsyncSession) -> "MessagingService":
        return cls(MessagingRepository(session), CaseRepository(session), session=session)

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_read(self, user: User) -> None:
        if not has_permission(user.role, MESSAGE_READ_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view messages",
            )

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, MESSAGE_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to send messages",
            )

    async def _get_case(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Case:
        case = await self._cases.get_by_id(case_id, organization_id=organization_id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )
        return case

    async def _resolve_client_id(self, case: Case, portal_client_id: uuid.UUID) -> uuid.UUID:
        if case.client_id is not None:
            if case.client_id != portal_client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Case is not linked to the portal client",
                )
            return case.client_id
        return portal_client_id

    async def _get_or_create_thread(
        self,
        *,
        organization_id: uuid.UUID,
        case: Case,
        client_id: uuid.UUID,
        created_by_id: uuid.UUID | None = None,
    ) -> MessageThread:
        thread = await self._messaging.get_thread_by_case(
            organization_id=organization_id,
            case_id=case.id,
        )
        if thread is not None:
            return thread

        thread = MessageThread(
            organization_id=organization_id,
            case_id=case.id,
            client_id=client_id,
            status=MessageThreadStatus.OPEN,
        )
        apply_audit_on_create(thread, created_by_id)
        return await self._messaging.create_thread(thread)

    async def get_status(self, user: User) -> MessagingCenterStatusResponse:
        self._require_read(user)
        self._require_organization(user)
        return get_messaging_center_status()

    async def get_case_thread(self, user: User, case_id: uuid.UUID) -> CaseMessageThreadResponse:
        self._require_read(user)
        organization_id = self._require_organization(user)
        await self._get_case(case_id, organization_id)

        thread = await self._messaging.get_thread_by_case(
            organization_id=organization_id,
            case_id=case_id,
        )
        messages: list[ThreadMessage] = []
        if thread is not None:
            messages = await self._messaging.list_messages(
                thread.id, organization_id=organization_id
            )
        return CaseMessageThreadResponse.from_thread(
            case_id=case_id,
            thread=thread,
            messages=messages,
        )

    async def post_staff_message(
        self,
        user: User,
        case_id: uuid.UUID,
        data: MessageCreate,
    ) -> ThreadMessageResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)
        case = await self._get_case(case_id, organization_id)
        if case.client_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Case must be linked to a client before messaging",
            )

        thread = await self._get_or_create_thread(
            organization_id=organization_id,
            case=case,
            client_id=case.client_id,
            created_by_id=user.id,
        )
        if thread.status == MessageThreadStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message thread is closed",
            )

        message = ThreadMessage(
            organization_id=organization_id,
            thread_id=thread.id,
            sender_role=MessageSenderRole.STAFF,
            staff_user_id=user.id,
            body=data.body,
        )
        message = await self._messaging.create_message(message)
        apply_audit_on_update(thread, user.id)
        await self._messaging.save_thread(thread)

        if self._session is not None:
            await publish_platform_event(
                self._session,
                staff_message_sent_event(thread, message, staff_user_id=user.id),
            )
            await dispatch_staff_message_push(
                self._session,
                organization_id=organization_id,
                case_id=case_id,
                client_id=case.client_id,
                thread_message_id=message.id,
                title="New message from your case team",
                body_preview=data.body[:500],
            )
            await self._session.commit()

        return ThreadMessageResponse.from_model(message)

    async def get_portal_case_thread(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
    ) -> CaseMessageThreadResponse:
        organization_id = portal_user.organization_id
        thread = await self._messaging.get_thread_by_case(
            organization_id=organization_id,
            case_id=case_id,
        )
        messages: list[ThreadMessage] = []
        if thread is not None:
            messages = await self._messaging.list_messages(
                thread.id, organization_id=organization_id
            )
        return CaseMessageThreadResponse.from_thread(
            case_id=case_id,
            thread=thread,
            messages=messages,
        )

    async def post_portal_message(
        self,
        portal_user: ClientPortalUser,
        case_id: uuid.UUID,
        data: MessageCreate,
    ) -> ThreadMessageResponse:
        organization_id = portal_user.organization_id
        case = await self._get_case(case_id, organization_id)
        client_id = await self._resolve_client_id(case, portal_user.client_id)

        thread = await self._get_or_create_thread(
            organization_id=organization_id,
            case=case,
            client_id=client_id,
        )
        if thread.status == MessageThreadStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message thread is closed",
            )

        message = ThreadMessage(
            organization_id=organization_id,
            thread_id=thread.id,
            sender_role=MessageSenderRole.PORTAL_CLIENT,
            portal_user_id=portal_user.id,
            body=data.body,
        )
        message = await self._messaging.create_message(message)
        await self._messaging.save_thread(thread)

        if self._session is not None:
            await publish_platform_event(
                self._session,
                portal_message_sent_event(thread, message, portal_user_id=portal_user.id),
            )
            await self._session.commit()

        return ThreadMessageResponse.from_model(message)
