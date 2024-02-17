from math import pi as _pi
from time import time as _time

from leads import Device as _Device


def rpm2kmh(rpm: float, wheel_circumference: float) -> float:
    return rpm * wheel_circumference * .0006


class WheelSpeedSensor(_Device):
    def __init__(self, wheel_diameter: int | float) -> None:
        super().__init__()
        self._wheel_circumference: float = wheel_diameter * 2.54 * _pi
        self._wheel_speed: int | float = 0
        self._last_valid: float = 0

    def update(self, data: int | float) -> None:
        self._wheel_speed = rpm2kmh(data, self._wheel_circumference)
        self._last_valid = _time()

    def read(self) -> float:
        # add .001 to avoid zero division
        d = rpm2kmh(60 / (.001 + _time() - self._last_valid), self._wheel_circumference)
        return 0 if d < 1 else d if d < 5 else self._wheel_speed
