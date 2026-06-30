"""Event bus unit tests."""

import uuid

import pytest
from verdin_event_bus import EventBus, PlatformEvent, get_event_bus, reset_event_bus, set_event_bus


@pytest.fixture(autouse=True)
def isolated_bus() -> None:
    reset_event_bus()
    yield
    reset_event_bus()


@pytest.mark.asyncio
async def test_event_bus_dispatches_to_subscriber() -> None:
    bus = EventBus()
    received: list[PlatformEvent] = []

    async def handler(event: PlatformEvent, _context: dict) -> None:
        received.append(event)

    bus.subscribe(handler)
    event = PlatformEvent(
        event_type="CASE_CREATED",
        event_category="case",
        title="Case created",
        organization_id=uuid.uuid4(),
        source_module="cases",
    )
    await bus.publish(event, context={})
    assert len(received) == 1
    assert received[0].event_type == "CASE_CREATED"


@pytest.mark.asyncio
async def test_event_bus_supports_sync_handlers_and_unsubscribe() -> None:
    bus = EventBus()
    received: list[str] = []

    def handler(event: PlatformEvent, _context: dict) -> None:
        received.append(event.event_type)

    unsubscribe = bus.subscribe(handler)
    event = PlatformEvent(
        event_type="TASK_CREATED",
        event_category="task",
        title="Task created",
        organization_id=uuid.uuid4(),
        source_module="tasks",
    )

    await bus.publish(event, context={})
    unsubscribe()
    await bus.publish(event, context={})

    assert received == ["TASK_CREATED"]
    assert bus.is_subscribed(handler) is False


def test_global_event_bus_singleton() -> None:
    first = get_event_bus()
    second = get_event_bus()
    assert first is second
    custom = EventBus()
    set_event_bus(custom)
    assert get_event_bus() is custom
