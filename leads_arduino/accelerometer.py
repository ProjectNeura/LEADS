from typing import override as _override

from leads import Device as _Device


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
    def read(self) -> tuple[float, float, float, float, float, float]:
        return self._yaw, self._pitch, self._roll, self._fa, self._la, self._va
