from copy import copy as _copy
from typing import TypeVar as _TypeVar, Generic as _Generic

from .data import DataContainer, DefaultDataContainer


T = _TypeVar("T")


def _check_data_type(data: T, superclass: type = DataContainer):
    if not isinstance(data, superclass):
        raise TypeError("`initial_data` must inherit from `DataContainer`")


class Context(_Generic[T]):
    def __init__(self, initial_data: T = DefaultDataContainer()):
        _check_data_type(initial_data)
        self.__initial_data_type: type = type(initial_data)
        self._data: T = initial_data

    def data(self) -> T:
        return _copy(self._data)

    def push(self, data: T):
        _check_data_type(data, self.__initial_data_type)
        self._data = data
