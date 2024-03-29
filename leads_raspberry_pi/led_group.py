from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from dataclasses import dataclass as _dataclass
from time import sleep as _sleep
from typing import override as _override

from leads import Controller as _Controller
from leads_raspberry_pi.led import LED, LEDCommand
from leads_raspberry_pi.types import TransitionDirection


class LEDGroupAnimation(object, metaclass=_ABCMeta):
    @_abstractmethod
    def do(self, command: LEDCommand, *leds: LED) -> None:
        raise NotImplementedError


class Entire(LEDGroupAnimation):
    @_override
    def do(self, command: LEDCommand, *leds: LED) -> None:
        for led in leds:
            led.write(command)


class Transition(LEDGroupAnimation):
    def __init__(self, direction: TransitionDirection, interval: float = 1) -> None:
        self._direction: TransitionDirection = direction
        self._interval: float = interval

    @_override
    def do(self, command: LEDCommand, *leds: LED) -> None:
        if self._direction == "left2right":
            for led in leds:
                led.write(command)
                _sleep(self._interval)
        elif self._direction == "right2left":
            for led in leds[::-1]:
                led.write(command)
                _sleep(self._interval)


@_dataclass
class LEDGroupCommand(object):
    command: LEDCommand
    animation: LEDGroupAnimation


class LEDGroup(_Controller):
    def __init__(self, *leds: LED) -> None:
        super().__init__()
        self._leds: tuple[LED, ...] = leds

    @_override
    def write(self, payload: LEDGroupCommand) -> None:
        payload.animation.do(payload.command, *self._leds)
