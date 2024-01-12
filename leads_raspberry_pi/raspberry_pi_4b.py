from RPi import GPIO as _GPIO

from leads import Controller as _Controller, controller as _controller, MAIN_CONTROLLER as _MAIN_CONTROLLER


@_controller(_MAIN_CONTROLLER)
class RaspberryPi4B(_Controller):
    async def initialize(self) -> None:
        _GPIO.setmode(_GPIO.BCM)

    def read(self) -> None:
        return None
