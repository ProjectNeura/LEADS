from typing import Callable as _Callable

from leads.context import Context
from leads.dt import Device
from leads.event import SuspensionEvent
from leads.logger import L


def mark_system(device: Device, system: str, *related: str) -> None:
    if hasattr(device, "__device_system__"):
        device.__setattr__("__device_system__", device.__getattribute__("__device_system__") + [system, *related])
    device.__setattr__("__device_system__", [system])


def read_marked_system(device: Device) -> list[str] | None:
    return device.__getattribute__("__device_system__") if hasattr(device, "__device_system__") else None


class SystemFailureTracer(object):
    def __init__(self) -> None:
        self._context: Context | None = None
        self.on_fail: _Callable[[Device, SuspensionEvent], None] = lambda _, __: None
        self.on_recover: _Callable[[Device, SuspensionEvent], None] = lambda _, __: None

    def fail(self, device: Device, e: Exception) -> None:
        if not (systems := read_marked_system(device)):
            raise RuntimeWarning("System not marked for device " + str(device))
        for system in systems:
            self.on_fail(device, SuspensionEvent(self._context, system, str(e)))
            L.error(f"{system} error: {e}")

    def recover(self, device: Device) -> None:
        if not (systems := read_marked_system(device)):
            raise RuntimeWarning("System not marked for device " + str(device))
        for system in systems:
            self.on_recover(device, SuspensionEvent(self._context, system, "Recovered"))
            L.info(system + " recovered")


SFT = SystemFailureTracer()
