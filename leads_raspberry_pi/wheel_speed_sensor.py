from math import floor as _floor
from time import time as _time

from RPi import GPIO as _GPIO

from leads import Device as _Device
from leads.data_persistence import DataPersistence as _DataPersistence


class WheelSpeedSensor(_Device):
    def __init__(self, *pins: int, reduction_factor: float = 1, wheel_radius: float = 1) -> None:
        super().__init__(*pins)
        self._pulses: _DataPersistence[float] = _DataPersistence(max_size=4, compressor=lambda seq, ts: seq[-ts:])
        self._reduction_factor: float = reduction_factor
        self._wheel_radius: float = wheel_radius

    def pulse(self) -> None:
        self._pulses.append(_time())

    def initialize(self, *parent_tags: str) -> None:
        self.pins_check(1)
        _GPIO.setup(self._pins[0], _GPIO.IN, pull_up_down=_GPIO.PUD_UP)
        _GPIO.add_event_detect(self._pins[0], _GPIO.FALLING, callback=self.pulse, bouncetime=20)
        self.pulse()

    def read(self) -> float:
        return _floor(60 * self._reduction_factor / (_time() - self._pulses[-1])) * self._wheel_radius
