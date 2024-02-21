from typing import Any as _Any, override as _override

from leads.context import Context
from leads.dt import Device
from leads.event import SuspensionEvent
from leads.plugin.plugin import Plugin


class SlfTst(Plugin):
    def __init__(self) -> None:
        super().__init__([])
        self.tracked_devices: list[Device] = []

    @_override
    def on_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        for device in self.tracked_devices:
            context.suspend(SuspensionEvent(
                context,
                device.__getattribute__("__slftst_system__"),
                device.__getattribute__("__slftst_cause__")
            ))

    def inject(self, device: Device, system: str, cause: str) -> None:
        device.__setattr__("__slftst__", True)
        device.__setattr__("__slftst_system__", system)
        device.__setattr__("__slftst_cause__", cause)
        self.tracked_devices.append(device)

    def deject(self, device: Device) -> None:
        device.__delattr__("__slftst__")
        device.__delattr__("__slftst_system__")
        device.__delattr__("__slftst_cause__")
        self.tracked_devices.remove(device)
