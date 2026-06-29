"""API event bus wiring and publish helpers."""

from sqlalchemy.ext.asyncio import AsyncSession
from verdin_event_bus import PlatformEvent, get_event_bus, publish

from api.modules.timeline.subscriber import persist_platform_event

_registered = False


def configure_event_bus() -> None:
    global _registered
    if _registered:
        return
    bus = get_event_bus()
    bus.subscribe(persist_platform_event)
    _registered = True


async def publish_platform_event(session: AsyncSession, event: PlatformEvent) -> None:
    configure_event_bus()
    await publish(event, context={"session": session})


def reset_event_bus_for_tests() -> None:
    global _registered
    from verdin_event_bus import reset_event_bus

    reset_event_bus()
    _registered = False
