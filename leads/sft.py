from typing import Callable as _Callable

from leads.dt import Device
from leads.event import SuspensionEvent
from leads.logger import L
from leads.registry import require_context


def mark_device(device: Device, system: str, *related: str, append: bool = True) -> None:
    setattr(device, "__sft_marker__", list(set(getattr(device, "__sft_marker__") + [
        system, *related] if append and hasattr(device, "__sft_marker__") else [system, *related])))


def read_device_marker(device: Device) -> list[str] | None:
    return getattr(device, "__sft_marker__") if hasattr(device, "__sft_marker__") else None


class SystemFailureTracer(object):
    def __init__(self) -> None:
        super().__init__()
        self.on_fail: _Callable[[SuspensionEvent], None] = lambda _: None
        self.on_recover: _Callable[[SuspensionEvent], None] = lambda _: None
        self.on_device_fail: _Callable[[Device, str | Exception], None] = lambda _, __: None
        self.on_device_recover: _Callable[[Device], None] = lambda _: None
        self._system_failures: dict[str, int] = {}

    def num_system_failures(self, system: str) -> int:
        return self._system_failures[system]

    def fail(self, device: Device, error: str | Exception) -> None:
        if isinstance(error, Exception):
            error = repr(error)
        if not (systems := read_device_marker(device)):
            raise RuntimeWarning(f"No system marked for device {device}")
        self.on_device_fail(device, error)
        L.error(f"{device} error: {error}")
        for system in systems:
            if system not in self._system_failures:
                self._system_failures[system] = 0
            self._system_failures[system] += 1
            self.on_fail(e := SuspensionEvent(context := require_context(), system, error))
            context.suspend(e)

    def recover(self, device: Device) -> None:
        if not (systems := read_device_marker(device)):
            raise RuntimeWarning(f"System not marked for device {device}")
        self.on_device_recover(device)
        L.debug(f"{device} recovered")
        for system in systems:
            if system not in self._system_failures:
                continue
            self._system_failures[system] -= 1
            if self._system_failures[system] > 0:
                continue
            self._system_failures.pop(system)
            self.on_recover(SuspensionEvent(require_context(), system, "Recovered"))


SFT: SystemFailureTracer = SystemFailureTracer()
