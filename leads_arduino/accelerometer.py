from dataclasses import dataclass as _dataclass
from typing import override as _override, Self as _Self

from numpy import ndarray as _ndarray, sin as _sin, cos as _cos, array as _array

from leads import Device as _Device, Serializable as _Serializable


def rotation_matrix(yaw: float, pitch: float, roll: float) -> _ndarray:
    sy, cy, sp, cp, sr, cr = _sin(yaw), _cos(yaw), _sin(pitch), _cos(pitch), _sin(roll), _cos(roll)
    return _array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]]) @ _array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]]) @ _array(
        [[1, 0, 0], [0, cr, -sr], [0, sr, cr]])


@_dataclass
class Acceleration(_Serializable):
    yaw: float
    pitch: float
    roll: float
    forward_acceleration: float
    lateral_acceleration: float
    vertical_acceleration: float

    def linear(self) -> _Self:
        fg = rotation_matrix(self.yaw, self.pitch, self.roll).T @ [0, 0, -9.8]
        return Acceleration(self.yaw, self.pitch, self.roll, self.forward_acceleration + fg[0],
                            self.lateral_acceleration + fg[1], self.vertical_acceleration + fg[2])


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
