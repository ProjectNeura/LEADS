from typing import TypeVar as _TypeVar

from .context import Context as _Context
from .data import DefaultDataContainer as _DefaultDataContainer
from .event import EventListener as _EventListener, UpdateEvent as _UpdateEvent


_T = _TypeVar("_T")


class Leads(_Context[_T]):
    def __init__(self, initial_data: _T = _DefaultDataContainer(), event_listener: _EventListener = _EventListener()):
        super().__init__(initial_data)
        self._event_listener: _EventListener = event_listener

    def set_event_listener(self, event_listener: _EventListener):
        self._event_listener = event_listener

    def update(self):
        self._event_listener.on_update(_UpdateEvent(self))
