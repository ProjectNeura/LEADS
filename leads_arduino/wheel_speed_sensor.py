from time import time as _time

from leads import Device as _Device


def rpm2kmh(rpm: float, wheel_radius: float) -> float:
    return rpm * wheel_radius * .0006


class WheelSpeedSensor(_Device):
    def __init__(self, wheel_radius: float) -> None:
        super().__init__()
        self._wheel_radius: float = wheel_radius
        self._wheel_speed: int | float = 0
        self._last_valid: float = 0

    def update(self, data: int | float) -> None:
        self._wheel_speed = rpm2kmh(data, self._wheel_radius)
        self._last_valid = _time()

    def read(self) -> float:
        return d if (d := rpm2kmh(60 / _time() - self._last_valid, self._wheel_speed)) < 5 else self._wheel_speed
