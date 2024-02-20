from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from collections import deque as _deque
from enum import IntEnum as _IntEnum
from time import time as _time
from typing import TypeVar as _TypeVar, Generic as _Generic

from numpy import diff as _diff, average as _average, array as _array

from leads.data import DataContainer, SRWDataContainer, DRWDataContainer

T = _TypeVar("T", bound=DataContainer)


class ECSMode(_IntEnum):
    STANDARD: int = 0x00
    AGGRESSIVE: int = 0x01
    SPORT: int = 0x02


def _check_data_type(data: T, superclass: type = DataContainer) -> None:
    if not isinstance(data, superclass):
        raise TypeError(f"New data must inherit from `{superclass}`")


class Context(_Generic[T], metaclass=_ABCMeta):
    def __init__(self,
                 srw_mode: bool = True,
                 initial_data: T | None = None,
                 data_seq_size: int = 100,
                 num_laps_recorded: int = 3) -> None:
        """
        :param srw_mode: True: single rear wheel mode; False: double rear wheel mode
        :param initial_data: initial data
        :param data_seq_size: buffer size of previous data
        """
        self._srw_mode: bool = srw_mode
        dct = SRWDataContainer if srw_mode else DRWDataContainer
        if initial_data:
            _check_data_type(initial_data, dct)
        else:
            initial_data = dct()
        self.__initial_data_type: type = type(initial_data)
        if data_seq_size < 1:
            raise ValueError("`data_seq_size` must be greater or equal to 1")
        self._data_seq: _deque[dct] = _deque((initial_data,), maxlen=data_seq_size)
        self._speed_seq: _deque[int | float] = _deque(maxlen=data_seq_size)
        self._lap_time_seq: _deque[int] = _deque((int(_time() * 1000),), maxlen=num_laps_recorded + 1)
        self._torque_mapping: list[float] = [1] if srw_mode else [1, 1]

    def data(self) -> T:
        """
        :return: a copy of the current data container
        """
        return self._data_seq[-1]

    def push(self, data: T) -> None:
        """
        Push new data into the sequence.
        :param data: the new data
        """
        _check_data_type(data, self.__initial_data_type)
        self._data_seq.append(data)
        self._speed_seq.append(data.speed)

    def srw_mode(self) -> bool:
        return self._srw_mode

    @_abstractmethod
    def update(self) -> None:
        raise NotImplementedError

    @_abstractmethod
    def intervene(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def record_lap(self) -> None:
        self._lap_time_seq.append(int(_time() * 1000))

    def get_lap_time_list(self) -> list[int]:
        return [self._lap_time_seq[i] - self._lap_time_seq[i - 1] for i in range(1, len(self._lap_time_seq))]

    def get_speed_trend(self) -> float:
        return float(_average(_diff(_array(self._speed_seq))))

    def torque_mapping(self, torque_mapping: list[float] | None = None) -> list[float] | None:
        if torque_mapping:
            self._torque_mapping = torque_mapping
        else:
            return self._torque_mapping

    def overwrite_throttle(self, force: float) -> float:
        # todo
        return 0

    def overwrite_brake(self, force: float) -> float:
        # todo
        return 0
