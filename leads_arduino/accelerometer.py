from dataclasses import dataclass as _dataclass
from typing import override as _override

from leads import Device as _Device, Serializable as _Serializable


@_dataclass
class Acceleration(_Serializable):
    yaw: float
    pitch: float
    roll: float
    forward_acceleration: float
    lateral_acceleration: float
    vertical_acceleration: float


class Accelerometer(_Device):
    def __init__(self) -> None:
        super().__init__()
        self._yaw: float = 0
        self._pitch: float = 0
        self._roll: float = 0
        self._fa: float = 0
        self._la: float = 0
        self._va: float = 0

    @_override
    def update(self, data: str) -> None:
        self._yaw, self._pitch, self._roll, self._fa, self._la, self._va = tuple(map(float, data.split(',')))

    @_override
    def read(self) -> Acceleration:
        return Acceleration(self._yaw, self._pitch, self._roll, self._fa, self._la, self._va)
