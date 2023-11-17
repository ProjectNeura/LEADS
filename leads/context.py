from typing import TypeVar as _TypeVar
from copy import deepcopy as _deepcopy

from .data import DataContainer as _Data
from .event import EventListener as _EventListener, UpdateEvent as _UpdateEvent


_T = _TypeVar("_T")


class Context(object):
    def __init__(self, event_listener: _EventListener, initial_data: _T = _Data()):
        self._event_listener: _EventListener = event_listener
        self._data: _T = initial_data

    def set_event_listener(self, event_listener: _EventListener):
        self._event_listener = event_listener

    def data(self) -> _T:
        return _deepcopy(self._data)

    def push(self, data: _Data):
        self._data = data

    def update(self):
        self._event_listener.on_update(_UpdateEvent(self))
