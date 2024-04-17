from typing import Callable as _Callable

from leads.dt import Device
from leads.event import SuspensionEvent
from leads.logger import L
from leads.registry import require_context


def mark_system(device: Device, system: str, *related: str) -> None:
    if hasattr(device, "__device_system__"):
        setattr(device, "__device_system__", getattr(device, "__device_system__") + related)
    setattr(device, "__device_system__", [system, *related])


def read_marked_system(device: Device) -> list[str] | None:
    return getattr(device, "__device_system__") if hasattr(device, "__device_system__") else None


class SystemFailureTracer(object):
    def __init__(self) -> None:
        super().__init__()
        self.on_fail: _Callable[[Device, SuspensionEvent], None] = lambda _, __: None
        self.on_recover: _Callable[[Device, SuspensionEvent], None] = lambda _, __: None

    def fail(self, device: Device, error: str | Exception) -> None:
        if isinstance(error, Exception):
            error = repr(error)
        if not (systems := read_marked_system(device)):
            raise RuntimeWarning(f"No system marked for device {device}")
        for system in systems:
            self.on_fail(device, e := SuspensionEvent(context := require_context(), system, error))
            context.suspend(e)
            L.error(f"{system} error: {error}")

    def recover(self, device: Device) -> None:
        if not (systems := read_marked_system(device)):
            raise RuntimeWarning(f"System not marked for device {device}")
        for system in systems:
            self.on_recover(device, SuspensionEvent(require_context(), system, "Recovered"))
            L.info(f"{system} recovered")


SFT: SystemFailureTracer = SystemFailureTracer()
