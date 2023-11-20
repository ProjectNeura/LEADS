from typing import TypeVar as _TypeVar, Generic as _Generic
from abc import abstractmethod as _abstractmethod, ABC as _ABC

from .device import Device


T = _TypeVar("T")


class Output(Device, _Generic[T]):
    @_abstractmethod
    def write(self, payload: T):
        raise NotImplementedError


class Motor(Output[T], _ABC):
    pass
