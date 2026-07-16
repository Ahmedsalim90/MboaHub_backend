from collections import defaultdict
from collections.abc import Awaitable, Callable

from pydantic import BaseModel

EventHandler = Callable[[BaseModel], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type[BaseModel], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type[BaseModel], handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: BaseModel) -> None:
        for handler in self._handlers[type(event)]:
            await handler(event)
