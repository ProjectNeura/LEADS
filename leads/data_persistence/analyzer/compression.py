from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from typing import overload as _overload, override as _override

from .._computational import array as _array, maximum as _maximum


class Compression(object, metaclass=_ABCMeta):
    @_overload
    def __init__(self, *args, **kwargs) -> None:  # real signature unknown
        raise NotImplementedError

    def __init__(self, channel_index: int) -> None:
        self._channel_index: int = channel_index

    @_abstractmethod
    def compress(self, data: _array) -> _array:
        raise NotImplementedError


class SpeedCompression(Compression):
    def __init__(self, channel_index: int = 1) -> None:
        super().__init__(channel_index)

    @_override
    def compress(self, data: _array) -> _array:
        speed_seq = data[:, data]
        data[:, data] = speed_seq / _maximum(speed_seq)
        return data
