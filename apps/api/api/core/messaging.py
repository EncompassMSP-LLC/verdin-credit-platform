"""Secure messaging status helpers."""

from api.modules.messaging.schemas import MessagingCenterStatusResponse

_MESSAGING_CAPABILITIES = [
    "case_scoped_threads",
    "portal_client_messages",
    "staff_replies",
    "org_scoped_message_history",
]

_DEFERRED_CAPABILITIES = [
    "real_time_push_notifications",
    "email_bridge",
    "attachment_support",
    "message_encryption_at_rest",
]


def get_messaging_center_status() -> MessagingCenterStatusResponse:
    return MessagingCenterStatusResponse(
        secure_messaging_enabled=True,
        thread_per_case=True,
        capabilities=list(_MESSAGING_CAPABILITIES),
        deferred_capabilities=list(_DEFERRED_CAPABILITIES),
    )
