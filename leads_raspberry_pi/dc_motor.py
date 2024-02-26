from typing import override as _override

from RPi.GPIO import setup, OUT

from leads import Device as _Device


class DCMotor(_Device):
    @_override
    def initialize(self, *parent_tags: str) -> None:
        setup(self._pins[0], OUT)
