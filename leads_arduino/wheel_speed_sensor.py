from time import time as _time
from typing import override as _override

from numpy import pi as _pi

from leads import Device as _Device, get_device as _get_device, Odometer as _Odometer
from leads_arduino.accelerometer import Accelerometer


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
    - Any Hall effect sensor (switch)
    """

    def __init__(self, wheel_diameter: float, num_divisions: int = 1, odometer_tag: str | None = None,
                 accelerometer_tag: str | None = None) -> None:
        super().__init__()
        self._wheel_circumference: float = wheel_diameter * 2.54 * _pi
        self._num_divisions: int = num_divisions
        self._wheel_speed: float = 0
        self._last_valid: float = 0
        self._odometer_tag: str | None = odometer_tag
        self._odometer: _Odometer | None = None
        self._accelerometer_tag: str | None = accelerometer_tag
        self._accelerometer: Accelerometer | None = None
        self._last_acceleration: float = 0

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        if self._odometer_tag:
            self._odometer = _get_device(self._odometer_tag)
            if not isinstance(self._odometer, _Odometer):
                raise TypeError(f"Unexpected odometer type: {type(self._odometer)}")
        if self._accelerometer_tag:
            self._accelerometer = _get_device(self._accelerometer_tag)
            if not isinstance(self._accelerometer, Accelerometer):
                raise TypeError(f"Unexpected accelerometer type: {type(self._accelerometer)}")

    @_override
    def update(self, data: str) -> None:
        t = _time()
        ws = rpm2kmh(float(data), self._wheel_circumference) / self._num_divisions
        if self._accelerometer and self._last_acceleration:
            a = self._accelerometer.read().linear().forward_acceleration
            v = (a + self._last_acceleration) * 1.8 * (t - self._last_valid)
            if abs((ws - self._wheel_speed - v) / (v + .0000000001)) > 1.5:
                return
            self._last_acceleration = a
        self._wheel_speed = ws
        self._last_valid = t
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
