"""Messaging timeline event types."""

from enum import StrEnum


class MessagingEventType(StrEnum):
    PORTAL_MESSAGE_SENT = "messaging.portal_message_sent"
    STAFF_MESSAGE_SENT = "messaging.staff_message_sent"
