from typing import Callable as _Callable

from leads.context import Context
from leads.dt import Device
from leads.event import SuspensionEvent


def mark_system(device: Device, system: str) -> None:
    device.__setattr__("__device_system__", system)


def read_marked_system(device: Device) -> str | None:
    return device.__getattribute__("__device_system__") if hasattr(device, "__device_system__") else None


class SystemStatusTracer(object):
    def __init__(self) -> None:
        self._context: Context | None = None
        self.on_fail: _Callable[[Device, SuspensionEvent], None] = lambda _, __: None

    def fail(self, device: Device, e: Exception) -> None:
        if not (system := read_marked_system(device)):
            raise RuntimeWarning("System not marked for device " + str(device))
        self.on_fail(device, SuspensionEvent(self._context, system, str(e)))
