from abc import abstractmethod as _abstractmethod
from typing import TypeVar as _TypeVar, Generic as _Generic

from .device import Device


T = _TypeVar("T")


class Controller(Device, _Generic[T]):
    def __init__(self, tag: str, level: int = 0):
        super().__init__(tag)
        self._level: int = level
        self._devices: dict[str, Device] = {}

    def attach_device(self, device: Device):
        self._devices[device.get_tag()] = device

    @_abstractmethod
    def collect_all(self) -> T:
        raise NotImplementedError
