from typing import TypeVar as _TypeVar

from .context import Context
from .event import EventListener, UpdateEvent

T = _TypeVar("T")


class Leads(Context[T]):
    def __init__(self, event_listener: EventListener = EventListener(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._event_listener: EventListener = event_listener

    def set_event_listener(self, event_listener: EventListener):
        self._event_listener = event_listener

    def update(self):
        self._event_listener.on_update(UpdateEvent(self))

