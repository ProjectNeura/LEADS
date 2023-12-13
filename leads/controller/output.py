from abc import abstractmethod as _abstractmethod, ABCMeta as _ABCMeta
from typing import TypeVar as _TypeVar, Generic as _Generic

from leads.controller.device import Device

T = _TypeVar("T")


class Output(Device, _Generic[T], metaclass=_ABCMeta):
    @_abstractmethod
    def write(self, payload: T) -> None:
        raise NotImplementedError


class Motor(Output[T], metaclass=_ABCMeta):
    pass
