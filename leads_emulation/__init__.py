from random import randint as _randint
from time import time as _time
from typing import override as _override

from numpy import sin as _sin, pi as _pi

from leads import Controller as _Controller, DataContainer as _DataContainer


class _EmulatedController(_Controller):
    def __init__(self,
                 minimum: int = 30,
                 maximum: int = 40,
                 skid_possibility: float = .1) -> None:
        super().__init__()
        self.minimum: int = minimum
        self.maximum: int = maximum
        self.skid_possibility: float = skid_possibility
        self._last_speed: float = 0
        self._last_time: float = _time()

    def generate_rear_wheel_speed(self, front_wheel_speed: float) -> float:
        return front_wheel_speed if self.skid_possibility <= 0 else front_wheel_speed + int(_randint(
            -int(1 / self.skid_possibility), int(1 / self.skid_possibility)) * self.skid_possibility)

    def generate_forward_acceleration(self, speed: float) -> float:
        t = _time()
        try:
            return (speed - self._last_speed) / 3.6 / (t - self._last_time)
        finally:
            self._last_speed = speed
            self._last_time = t


class RandomController(_EmulatedController):
    @_override
    def read(self) -> _DataContainer:
        return _DataContainer(voltage=48.0,
                              speed=(fws := _randint(self.minimum, self.maximum)),
                              front_wheel_speed=fws,
                              rear_wheel_speed=self.generate_rear_wheel_speed(fws),
                              forward_acceleration=self.generate_forward_acceleration(fws),
                              gps_valid=True,
                              gps_ground_speed=fws,
                              latitude=_randint(4315, 4415) / 100,
                              longitude=-_randint(7888, 7988) / 100)


class SinController(_EmulatedController):
    def __init__(self,
                 minimum: int = 30,
                 maximum: int = 40,
                 skid_possibility: float = .1,
                 acceleration: float = .01) -> None:
        super().__init__(minimum, maximum, skid_possibility)
        self.acceleration: float = acceleration
        self.magnitude: int = int((maximum - minimum) * .5)
        self.counter: float = 0

    @_override
    def read(self) -> _DataContainer:
        try:
            return _DataContainer(voltage=48.0,
                                  speed=(fws := (_sin(self.counter) * self.magnitude + self.magnitude)),
                                  front_wheel_speed=fws,
                                  rear_wheel_speed=self.generate_rear_wheel_speed(fws),
                                  forward_acceleration=self.generate_forward_acceleration(fws),
                                  gps_valid=True,
                                  gps_ground_speed=fws,
                                  latitude=_randint(4315, 4415) / 100,
                                  longitude=-_randint(7888, 7988) / 100)
        finally:
            self.counter = (self.counter + self.acceleration) % (2 * _pi)
