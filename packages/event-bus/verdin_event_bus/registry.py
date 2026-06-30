"""Event bus registry and dispatch."""

import inspect
from collections.abc import Callable

from verdin_event_bus.event import PlatformEvent
from verdin_event_bus.subscriber import EventHandler


class EventBus:
    """In-process publish/subscribe event bus."""

    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []

    def subscribe(self, handler: EventHandler) -> Callable[[], None]:
        self._handlers.append(handler)

        def unsubscribe() -> None:
            self._handlers.remove(handler)

        return unsubscribe

    def is_subscribed(self, handler: EventHandler) -> bool:
        return handler in self._handlers

    async def publish(self, event: PlatformEvent, *, context: dict | None = None) -> None:
        payload = context or {}
        for handler in self._handlers:
            result = handler(event, payload)
            if inspect.isawaitable(result):
                await result

    def clear(self) -> None:
        self._handlers.clear()
