from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from collections import deque as _deque
from time import time as _time
from typing import TypeVar as _TypeVar, Generic as _Generic

from numpy import diff as _diff, average as _average, array as _array

from leads.constant import ESCMode
from leads.data import DataContainer

T = _TypeVar("T", bound=DataContainer)


def _check_data_type(data: T, superclass: type[DataContainer] = DataContainer) -> None:
    if not isinstance(data, superclass):
        raise TypeError(f"New data must inherit from `{superclass}`")


class Context(_Generic[T], metaclass=_ABCMeta):
    def __init__(self,
                 initial_data: T | None = None,
                 data_seq_size: int = 100,
                 num_laps_timed: int = 3) -> None:
        """
        :param initial_data: initial data
        :param data_seq_size: buffer size of history data
        :param num_laps_timed: number of timed laps retained
        """
        if initial_data:
            _check_data_type(initial_data, DataContainer)
        else:
            initial_data = DataContainer()
        self._initial_data_type: type[DataContainer] = type(initial_data)
        if data_seq_size < 1:
            raise ValueError("`data_seq_size` must be greater or equal to 1")
        self._data_seq: _deque[DataContainer] = _deque((initial_data,), maxlen=data_seq_size)
        self._speed_seq: _deque[float] = _deque(maxlen=data_seq_size)
        self._lap_time_seq: _deque[int] = _deque((int(_time() * 1000),), maxlen=num_laps_timed + 1)
        self._esc_mode: ESCMode = ESCMode.STANDARD
        self._left_indicator: bool = False
        self._right_indicator: bool = False
        self._hazard: bool = False

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
        _check_data_type(data, self._initial_data_type)
        self._data_seq.append(data)
        self._speed_seq.append(data.speed)

    def esc_mode(self, esc_mode: ESCMode | None = None) -> ESCMode | None:
        if esc_mode is None:
            return self._esc_mode
        self._esc_mode = esc_mode

    @_abstractmethod
    def update(self) -> None:
        raise NotImplementedError

    @_abstractmethod
    def intervene(self, *args, **kwargs) -> None:  # real signature unknown
        raise NotImplementedError

    @_abstractmethod
    def suspend(self, *args, **kwargs) -> None:  # real signature unknown
        raise NotImplementedError

    def time_lap(self) -> None:
        self._lap_time_seq.append(int(_time() * 1000))

    def lap_time_list(self) -> list[int]:
        return [self._lap_time_seq[i] - self._lap_time_seq[i - 1] for i in range(1, len(self._lap_time_seq))]

    def speed_trend(self) -> float:
        return float(_average(_diff(_array(self._speed_seq)))) if len(self._speed_seq) > 1 else 0

    def left_indicator(self, left_indicator: bool | None = None, override: bool = False) -> bool | None:
        if self._hazard and not override:
            return True
        if left_indicator is None:
            return self._left_indicator
        self._left_indicator = left_indicator

    def right_indicator(self, right_indicator: bool | None = None, override: bool = False) -> bool | None:
        if self._hazard and not override:
            return True
        if right_indicator is None:
            return self._right_indicator
        self._right_indicator = right_indicator

    def hazard(self, hazard: bool | None = None) -> bool | None:
        if hazard is None:
            return self._hazard
        self.left_indicator(hazard, True)
        self.right_indicator(hazard, True)
        self._hazard = hazard
