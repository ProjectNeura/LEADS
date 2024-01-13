from math import sin as _sin, pi as _pi
from random import randint as _randint

from leads import Controller as _Controller, SRWDataContainer as _SRWDataContainer, \
    DRWDataContainer as _DRWDataContainer


class _EmulatedController(_Controller):
    def __init__(self,
                 minimum: int = 30,
                 maximum: int = 40,
                 skid_possibility: float = .1) -> None:
        super().__init__()
        self.minimum: int = minimum
        self.maximum: int = maximum
        self.skid_possibility: float = skid_possibility

    def generate_rear_wheel_speed(self, front_wheel_speed: int | float) -> int | float:
        return front_wheel_speed + int(_randint(1, int(1 / self.skid_possibility)) * self.skid_possibility)


class SRWRandom(_EmulatedController):
    def read(self) -> _SRWDataContainer:
        return _SRWDataContainer(fws := _randint(self.minimum, self.maximum), self.generate_rear_wheel_speed(fws))


class DRWRandom(_EmulatedController):
    def read(self) -> _DRWDataContainer:
        return _DRWDataContainer(fws := _randint(self.minimum, self.maximum),
                                 rws := self.generate_rear_wheel_speed(fws),
                                 rws)


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
    def read(self) -> _SRWDataContainer:
        try:
            return _SRWDataContainer(fws := (_sin(self.counter) + .5) * self.magnitude + self.offset,
                                     self.generate_rear_wheel_speed(fws))
        finally:
            self.counter = (self.counter + self.acceleration) % _pi


class DRWSin(_SinController):
    def read(self) -> _DRWDataContainer:
        try:
            return _DRWDataContainer(fws := (_sin(self.counter) + .5) * self.magnitude + self.offset,
                                     rws := self.generate_rear_wheel_speed(fws),
                                     rws)
        finally:
            self.counter = (self.counter + self.acceleration) % _pi
