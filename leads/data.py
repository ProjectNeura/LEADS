from threading import Lock as _Lock
from typing import Self as _Self, Any as _Any
from abc import abstractmethod as _abstractmethod


class DataContainer(object):
    def __init__(self):
        self._lock: _Lock = _Lock()

    @_abstractmethod
    def __sub__(self, other: _Self) -> _Self:
        raise NotImplementedError

    def __setattr__(self, key: str, value: _Any):
        if key == "_lock":
            super().__setattr__(key, value)
            return
        self._lock.acquire()
        try:
            super().__setattr__(key, value)
        finally:
            self._lock.release()


class DefaultDataContainer(DataContainer):
    def __init__(self, wheel_speed: float = 0):
        super().__init__()
        self.wheel_speed: int | float = wheel_speed

    def __sub__(self, other: _Self) -> _Self:
        return DefaultDataContainer(self.wheel_speed - other.wheel_speed)
