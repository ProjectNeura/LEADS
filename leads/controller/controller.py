from abc import abstractmethod as _abstractmethod, ABCMeta as _ABCMeta
from typing import TypeVar as _TypeVar, Generic as _Generic

from leads.controller.device import Device

T = _TypeVar("T")


class Controller(Device, _Generic[T], metaclass=_ABCMeta):
    def __init__(self, tag: str, level: int = 0) -> None:
        super().__init__(tag)
        self._level: int = level
        self._devices: dict[str, Device] = {}

    def _attach_device(self, device: Device) -> None:
        self._devices[device.tag()] = device

    def device(self, tag: str) -> [Device]:
        return self._devices[tag]

    @_abstractmethod
    def collect_all(self) -> T:
        raise NotImplementedError
