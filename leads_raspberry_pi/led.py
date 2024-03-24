from typing import override as _override, Literal as _Literal

from gpiozero import LED as _LED

from leads import Device as _Device


class LED(_Device):
    def __init__(self, pin: int) -> None:
        super().__init__(pin)
        self._led: _LED = _LED(pin)

    @_override
    def read(self) -> bool:
        return self._led.is_active

    @_override
    def write(self, payload: _Literal[0, 1, 2]) -> None:
        if payload == 0:
            self._led.off()
        elif payload == 1:
            self._led.on()
        elif payload == 2:
            self._led.blink()
        else:
            raise ValueError("Invalid payload: " + str(payload))
