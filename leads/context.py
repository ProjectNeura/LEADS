from typing import TypeVar as _TypeVar, Generic as _Generic
from copy import copy as _copy

from .data import DataContainer as _Data, DefaultDataContainer as _DefaultDataContainer


_T = _TypeVar("_T")


def _check_data_type(data: _T, superclass: type = _Data):
    if not isinstance(data, superclass):
        raise TypeError("`initial_data` must inherit from `DataContainer`")


class Context(_Generic[_T]):
    def __init__(self, initial_data: _T = _DefaultDataContainer()):
        _check_data_type(initial_data)
        self.__initial_data_type: type = type(initial_data)
        self._data: _T = initial_data

    def data(self) -> _T:
        return _copy(self._data)

    def push(self, data: _T):
        _check_data_type(data, self.__initial_data_type)
        self._data = data
