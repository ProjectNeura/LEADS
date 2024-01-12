from time import time as _time

from RPi import GPIO as _GPIO

from leads import Device as _Device
from leads.data_persistence import DataPersistence as _DataPersistence


class WheelSpeedSensor(_Device):
    _start: float = .0
    _elapse: _DataPersistence[float] = _DataPersistence(max_size=8)

    def reset_time(self) -> None:
        self._start = _time()

    def pulse(self) -> None:
        self._elapse.append(_time() - self._start)
        self.reset_time()

    async def initialize(self, *parent_tags: str) -> None:
        self.pins_check(1)
        _GPIO.setup(self._pins[0], _GPIO.IN, pull_up_down=_GPIO.PUD_UP)
        _GPIO.add_event_detect(self._pins[0], _GPIO.FALLING, callback=self.pulse, bouncetime=20)
        self.reset_time()

    def read(self) -> float:
        return .0
