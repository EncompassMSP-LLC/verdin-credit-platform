"""Event subscriber protocol."""

from collections.abc import Awaitable, Callable
from typing import Any

from verdin_event_bus.event import PlatformEvent

EventHandler = Callable[[PlatformEvent, dict[str, Any]], Awaitable[None] | None]
