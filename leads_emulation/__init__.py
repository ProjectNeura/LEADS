from random import randint as _randint
from typing import override as _override

from numpy import sin as _sin, pi as _pi

from leads import Controller as _Controller, SRWDataContainer as _SRWDataContainer, \
    DRWDataContainer as _DRWDataContainer, Device as _Device


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


class SRWRandom(_EmulatedController):
    @_override
    def read(self) -> _SRWDataContainer:
        return _SRWDataContainer(voltage=48.0,
                                 min_speed=(fws := _randint(self.minimum, self.maximum)),
                                 front_wheel_speed=fws,
                                 rear_wheel_speed=self.generate_rear_wheel_speed(fws))


class DRWRandom(_EmulatedController):
    @_override
    def read(self) -> _DRWDataContainer:
        return _DRWDataContainer(voltage=48.0,
                                 min_speed=(fws := _randint(self.minimum, self.maximum)),
                                 front_wheel_speed=fws,
                                 left_rear_wheel_speed=(rws := self.generate_rear_wheel_speed(fws)),
                                 right_rear_wheel_speed=rws)


class _SinController(_EmulatedController):
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


class SRWSin(_SinController):
    @_override
    def read(self) -> _SRWDataContainer:
        try:
            return _SRWDataContainer(voltage=48.0,
                                     min_speed=(fws := (_sin(self.counter) + .5) * self.magnitude + self.offset),
                                     front_wheel_speed=fws,
                                     rear_wheel_speed=self.generate_rear_wheel_speed(fws))
        finally:
            self.counter = (self.counter + self.acceleration) % _pi


class DRWSin(_SinController):
    @_override
    def read(self) -> _DRWDataContainer:
        try:
            return _DRWDataContainer(voltage=48.0,
                                     min_speed=(fws := (_sin(self.counter) + .5) * self.magnitude + self.offset),
                                     front_wheel_speed=fws,
                                     left_rear_wheel_speed=(rws := self.generate_rear_wheel_speed(fws)),
                                     right_rear_wheel_speed=rws)
        finally:
            self.counter = (self.counter + self.acceleration) % _pi


class GPSReceiver(_Device):
    @_override
    def read(self) -> [bool, float, float, float, int, int]:
        return False, 0, 0, 0, 0, 0
