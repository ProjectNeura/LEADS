from copy import copy as _copy
from typing import TypeVar as _TypeVar, Generic as _Generic

from .constant import SYSTEM_DTCS, SYSTEM_ABS, SYSTEM_EBI, SYSTEM_ATBS
from .data import DataContainer, SRWDataContainer, DRWDataContainer

T = _TypeVar("T")


def _check_data_type(data: T, superclass: type = DataContainer):
    if not isinstance(data, superclass):
        raise TypeError(f"New data must inherit from `{superclass}`")


class Context(_Generic[T]):
    def __init__(self, srw_mode: bool = True, initial_data: T | None = None):
        """
        :param srw_mode: True: single rear wheel mode; False: double rear wheel mode
        :param initial_data: initial data
        """
        self._srw_mode: bool = srw_mode
        superclass = SRWDataContainer if srw_mode else DRWDataContainer
        if initial_data is None:
            initial_data = superclass()
        _check_data_type(initial_data, superclass)
        self.__initial_data_type: type = type(initial_data)
        self._data: T = initial_data
        self._dtcs: bool = True
        self._abs: bool = True
        self._ebi: bool = True
        self._atbs: bool = True

    def data(self) -> T:
        return _copy(self._data)

    def push(self, data: T):
        _check_data_type(data, self.__initial_data_type)
        self._data = data

    def set_subsystem(self, system: str, enabled: bool):
        if system == SYSTEM_DTCS:
            self.set_dtcs(enabled)
        elif system == SYSTEM_ABS:
            self.set_abs(enabled)
        elif system == SYSTEM_EBI:
            self.set_ebi(enabled)
        elif system == SYSTEM_ATBS:
            self.set_atbs(enabled)

    def in_srw_mode(self) -> bool:
        return self._srw_mode

    def set_dtcs(self, enabled: bool):
        self._dtcs = enabled

    def is_dtcs_enabled(self) -> bool:
        return self._dtcs

    def set_abs(self, enabled: bool):
        self._abs = enabled

    def is_abs_enabled(self) -> bool:
        return self._abs

    def set_ebi(self, enabled: bool):
        self._ebi = enabled

    def is_ebi_enabled(self) -> bool:
        return self._ebi

    def set_atbs(self, enabled: bool):
        self._atbs = enabled

    def is_atbs_enabled(self) -> bool:
        return self._atbs
