from typing import Callable as _Callable

from leads.dt import Device


def mark_system(device: Device, system: str) -> None:
    device.__setattr__("__device_system__", system)


def read_marked_system(device: Device) -> str | None:
    return device.__getattribute__("__device_system__") if hasattr(device, "__device_system__") else None


class SystemStatusTracer(object):
    def __init__(self) -> None:
        self.on_fail: _Callable[[Device, str, ], None]
