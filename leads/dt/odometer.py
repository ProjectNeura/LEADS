from threading import Lock as _Lock
from typing import override as _override

from leads.dt.device import Device


class Odometer(Device):
    def __init__(self) -> None:
        super().__init__()
        self._mileage: float = 0

    @_override
    def write(self, payload: float) -> None:
        self._mileage += payload

    @_override
    def read(self) -> float:
        return self._mileage


class ConcurrentOdometer(Odometer):
    def __init__(self) -> None:
        super().__init__()
        self._lock: _Lock = _Lock()

    @_override
    def write(self, payload: float) -> None:
        self._lock.acquire()
        try:
            super().write(payload)
        finally:
            self._lock.release()
