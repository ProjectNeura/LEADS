from typing import TypeVar as _TypeVar, Generic as _Generic
from abc import abstractmethod as _abstractmethod, ABCMeta as _ABCMeta

from .device import Device


T = _TypeVar("T")


class Output(Device, _Generic[T], metaclass=_ABCMeta):
    @_abstractmethod
    def write(self, payload: T):
        raise NotImplementedError


class Motor(Output[T], metaclass=_ABCMeta):
    pass
