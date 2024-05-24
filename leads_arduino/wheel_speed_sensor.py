from time import time as _time
from typing import override as _override

from numpy import pi as _pi

from leads import Device as _Device, get_device as _get_device, Odometer as _Odometer


def rpm2kmh(rpm: float, wheel_circumference: float) -> float:
    """
    :param rpm: revolutions per minute
    :param wheel_circumference: wheel circumference in centimeters
    :return: speed in kilometers per hour
    """
    return rpm * wheel_circumference * .0006


class WheelSpeedSensor(_Device):
    """
    See LEADS-Arduino.

    Supports:
    - Any hall effect sensor (switch)
    """

    def __init__(self, wheel_diameter: float, num_divisions: int = 1, odometer_tag: str | None = None) -> None:
        super().__init__()
        self._wheel_circumference: float = wheel_diameter * 2.54 * _pi
        self._num_divisions: int = num_divisions
        self._wheel_speed: float = 0
        self._last_valid: float = 0
        self._odometer_tag: str | None = odometer_tag
        self._odometer: _Odometer | None = None

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        if self._odometer_tag:
            self._odometer = _get_device(self._odometer_tag)

    @_override
    def update(self, data: str) -> None:
        if data.startswith(self._tag):
            self._wheel_speed = rpm2kmh(float(data[data.find(":") + 1:]),
                                        self._wheel_circumference) / self._num_divisions
            self._last_valid = _time()
            if self._odometer:
                self._odometer.write(self._wheel_circumference * .00001)

    @_override
    def read(self) -> float:
        """
        :return: speed in kilometers per hour
        """
        # add .0000000001 to avoid zero division
        r = rpm2kmh(60 / (.0000000001 + _time() - self._last_valid), self._wheel_circumference) / self._num_divisions
        return 0 if r < .1 else r if r < 5 else self._wheel_speed
