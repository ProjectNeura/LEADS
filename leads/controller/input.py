from abc import abstractmethod as _abstractmethod, ABCMeta as _ABCMeta
from typing import TypeVar as _TypeVar, Generic as _Generic

from .device import Device

T = _TypeVar("T")


class Input(Device, _Generic[T], metaclass=_ABCMeta):
    @_abstractmethod
    def read(self) -> T:
        raise NotImplementedError


class Sensor(Input[T], metaclass=_ABCMeta):
    pass


class WheelSpeedSensor(Sensor[float], metaclass=_ABCMeta):
    pass


class Camera(Sensor[bytes], metaclass=_ABCMeta):
    pass
