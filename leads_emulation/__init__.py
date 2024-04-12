from random import randint as _randint
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

    def generate_rear_wheel_speed(self, front_wheel_speed: float) -> float:
        return front_wheel_speed + int(_randint(1, int(1 / self.skid_possibility)) * self.skid_possibility)


class RandomController(_EmulatedController):
    @_override
    def read(self) -> _DataContainer:
        return _DataContainer(voltage=48.0,
                              speed=(fws := _randint(self.minimum, self.maximum)),
                              front_wheel_speed=fws,
                              rear_wheel_speed=self.generate_rear_wheel_speed(fws),
                              gps_valid=True,
                              gps_ground_speed=fws,
                              latitude=_randint(4315, 4415) / 100,
                              longitude=-_randint(7888, 7988) / 100)


class SinController(_EmulatedController):
    def __init__(self,
                 minimum: int = 30,
                 maximum: int = 40,
                 skid_possibility: float = .1,
                 acceleration: float = .05) -> None:
        super().__init__(minimum, maximum, skid_possibility)
        self.acceleration: float = acceleration
        self.magnitude: int = int((maximum - minimum) * .5)
        self.offset: int = minimum
        self.counter: float = 0

    @_override
    def read(self) -> _DataContainer:
        try:
            return _DataContainer(voltage=48.0,
                                  speed=(fws := (_sin(self.counter) + .5) * self.magnitude + self.offset),
                                  front_wheel_speed=fws,
                                  rear_wheel_speed=self.generate_rear_wheel_speed(fws),
                                  gps_valid=True,
                                  gps_ground_speed=fws,
                                  latitude=_randint(4315, 4415) / 100,
                                  longitude=-_randint(7888, 7988) / 100)
        finally:
            self.counter = (self.counter + self.acceleration) % _pi
