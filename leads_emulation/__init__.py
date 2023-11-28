from math import sin as _sin, pi as _pi
from random import randint as _randint

from leads import Controller as _Controller, SRWDataContainer as _SRWDataContainer, \
    DRWDataContainer as _DRWDataContainer


class SRWRandom(_Controller):
    def __init__(self, tag: str, minimum: int = 30, maximum: int = 40):
        super().__init__(tag)
        self.minimum: int = minimum
        self.maximum: int = maximum

    def collect_all(self) -> _SRWDataContainer:
        return _SRWDataContainer(ws := _randint(self.minimum, self.maximum), ws)


class DRWRandom(_Controller):
    def __init__(self, tag: str, minimum: int = 30, maximum: int = 40):
        super().__init__(tag)
        self.minimum: int = minimum
        self.maximum: int = maximum

    def collect_all(self) -> _DRWDataContainer:
        return _DRWDataContainer(ws := _randint(self.minimum, self.maximum), ws, ws)


class SRWSin(_Controller):
    def __init__(self, tag: str, minimum: int = 30, maximum: int = 40, acceleration: float = .05):
        super().__init__(tag)
        self.acceleration: float = acceleration
        self.magnitude: int = int((maximum - minimum) * .5)
        self.offset: int = minimum
        self.counter: float = 0

    def collect_all(self) -> _SRWDataContainer:
        try:
            return _SRWDataContainer(ws := int((_sin(self.counter) + .5) * self.magnitude + self.offset), ws)
        finally:
            self.counter = (self.counter + self.acceleration) % _pi
