"""Event bus publisher helpers."""

from verdin_event_bus.event import PlatformEvent
from verdin_event_bus.registry import EventBus

_global_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus()
    return _global_bus


def set_event_bus(bus: EventBus) -> None:
    global _global_bus
    _global_bus = bus


def reset_event_bus() -> None:
    global _global_bus
    _global_bus = None


async def publish(event: PlatformEvent, *, context: dict | None = None) -> None:
    await get_event_bus().publish(event, context=context)
