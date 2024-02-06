from collections import deque as _deque
from copy import copy as _copy
from typing import TypeVar as _TypeVar, Generic as _Generic

from leads.constant import SYSTEM_DTCS, SYSTEM_ABS, SYSTEM_EBI, SYSTEM_ATBS
from leads.data import DataContainer, SRWDataContainer, DRWDataContainer

T = _TypeVar("T", bound=DataContainer)


def _check_data_type(data: T, superclass: type = DataContainer) -> None:
    if not isinstance(data, superclass):
        raise TypeError(f"New data must inherit from `{superclass}`")


class Context(_Generic[T]):
    def __init__(self, srw_mode: bool = True, initial_data: T | None = None, data_seq_size: int = 1000) -> None:
        """
        :param srw_mode: True: single rear wheel mode; False: double rear wheel mode
        :param initial_data: initial data
        :param data_seq_size: buffer size of previous data
        """
        self._srw_mode: bool = srw_mode
        superclass = SRWDataContainer if srw_mode else DRWDataContainer
        if not initial_data:
            initial_data = superclass()
        _check_data_type(initial_data, superclass)
        self.__initial_data_type: type = type(initial_data)
        if data_seq_size < 1:
            raise ValueError("`data_seq_size` must be greater or equal to 1")
        self._data_seq: _deque = _deque((initial_data,), maxlen=data_seq_size)
        self._dtcs: bool = True
        self._abs: bool = True
        self._ebi: bool = True
        self._atbs: bool = True

    def data(self) -> T:
        """
        :return: a copy of the current data container
        """
        return _copy(self._data_seq[-1])

    def push(self, data: T) -> None:
        """
        Push new data into the sequence.
        :param data: the new data
        """
        _check_data_type(data, self.__initial_data_type)
        self._data_seq.append(data)

    def set_subsystem(self, system: str, enabled: bool) -> None:
        """
        Set a certain subsystem enabled or disabled.
        :param system: subsystem id
        :param enabled: True: enabled; False: disabled
        """
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

    def set_dtcs(self, enabled: bool) -> None:
        self._dtcs = enabled

    def is_dtcs_enabled(self) -> bool:
        return self._dtcs

    def set_abs(self, enabled: bool) -> None:
        self._abs = enabled

    def is_abs_enabled(self) -> bool:
        return self._abs

    def set_ebi(self, enabled: bool) -> None:
        self._ebi = enabled

    def is_ebi_enabled(self) -> bool:
        return self._ebi

    def set_atbs(self, enabled: bool) -> None:
        self._atbs = enabled

    def is_atbs_enabled(self) -> bool:
        return self._atbs

    def brake(self, force: float) -> int:
        # todo
        return 0
