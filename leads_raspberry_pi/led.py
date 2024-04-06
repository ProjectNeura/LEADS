from enum import IntEnum as _IntEnum
from typing import override as _override

from gpiozero import LED as _LED

from leads import Device as _Device


class LEDCommand(_IntEnum):
    OFF: int = 0
    ON: int = 1
    BLINK: int = 2
    BLINK_ONCE: int = 3


class LED(_Device):
    """
    Control a LED digitally.
    Supports:
    - Any 2-pin LED
    """
    def __init__(self, pin: int, blink_time_on: float = 1, blink_time_off: float = 1) -> None:
        super().__init__(pin)
        self._led: _LED = _LED(pin)
        self._blink_time_on: float = blink_time_on
        self._blink_time_off: float = blink_time_off

    @_override
    def read(self) -> bool:
        return self._led.is_active

    @_override
    def write(self, payload: LEDCommand) -> None:
        if payload == LEDCommand.OFF:
            self._led.off()
        elif payload == LEDCommand.ON:
            self._led.on()
        elif payload == LEDCommand.BLINK:
            self._led.blink(self._blink_time_on, self._blink_time_off)
        elif payload == LEDCommand.BLINK_ONCE:
            self._led.blink(self._blink_time_on, self._blink_time_off, 1)
