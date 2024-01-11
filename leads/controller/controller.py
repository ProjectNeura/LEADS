from abc import abstractmethod as _abstractmethod, ABCMeta as _ABCMeta
from typing import Any as _Any

from leads.controller.device import Device


class Controller(Device, metaclass=_ABCMeta):
    def __init__(self, level: int = 0) -> None:
        super().__init__()
        self._level: int = level
        self._devices: dict[str, Device] = {}

    async def _attach_device(self, tag: str, device: Device) -> None:
        self._devices[tag] = device
        device.tag(tag)
        await device.initialize()

    def device(self, tag: str, device: Device | None = None) -> Device | None:
        if device:
            self._attach_device(tag, device)
        else:
            return self._devices[tag]

    @_abstractmethod
    def read(self) -> _Any:
        raise NotImplementedError

    def write(self, payload: _Any) -> None:
        raise NotImplementedError
