"""API event bus wiring and publish helpers."""

from sqlalchemy.ext.asyncio import AsyncSession
from verdin_event_bus import PlatformEvent, get_event_bus, publish

from api.modules.timeline.subscriber import persist_platform_event


def configure_event_bus() -> None:
    """Subscribe the timeline persister to the current global event bus.

    Idempotent and resilient to the global bus being replaced (e.g. in tests
    that call ``reset_event_bus``): the subscription is checked against the
    bus instance in use rather than a module-level flag, so the persister is
    always (re)attached to whichever bus is currently active.
    """
    bus = get_event_bus()
    if bus.is_subscribed(persist_platform_event):
        return
    bus.subscribe(persist_platform_event)


async def publish_platform_event(session: AsyncSession, event: PlatformEvent) -> None:
    configure_event_bus()
    await publish(event, context={"session": session})


def reset_event_bus_for_tests() -> None:
    from verdin_event_bus import reset_event_bus

    reset_event_bus()
