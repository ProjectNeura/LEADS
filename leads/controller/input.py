from typing import TypeVar as _TypeVar, Generic as _Generic
from abc import abstractmethod as _abstractmethod, ABC as _ABC

from .device import Device


T = _TypeVar("T")


class Input(Device, _Generic[T]):
    @_abstractmethod
    def read(self) -> T:
        raise NotImplementedError


class Sensor(Input[T], _ABC):
    pass


class WheelSpeedSensor(Sensor[float], _ABC):
    pass


class Camera(Sensor[bytes], _ABC):
    pass
