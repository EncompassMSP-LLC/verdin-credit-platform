"""Secure messaging status helpers."""

from api.modules.messaging.schemas import MessagingCenterStatusResponse

_MESSAGING_CAPABILITIES = [
    "case_scoped_threads",
    "portal_client_messages",
    "staff_replies",
    "org_scoped_message_history",
    "portal_web_push",
    "attachment_support",
]

_DEFERRED_CAPABILITIES = [
    "websocket_live_feed",
    "email_bridge",
    "message_encryption_at_rest",
    "external_malware_engine",
]


def get_messaging_center_status() -> MessagingCenterStatusResponse:
    return MessagingCenterStatusResponse(
        secure_messaging_enabled=True,
        thread_per_case=True,
        capabilities=list(_MESSAGING_CAPABILITIES),
        deferred_capabilities=list(_DEFERRED_CAPABILITIES),
    )
