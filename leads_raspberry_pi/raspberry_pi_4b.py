from typing import Any as _Any

from leads import Controller as _Controller, Device as _Device, controller as _controller, device as _device, \
    MAIN_CONTROLLER as _MAIN_CONTROLLER, LEFT_FRONT_WHEEL_SPEED_SENSOR as _LEFT_FRONT_WHEEL_SPEED_SENSOR, \
    RIGHT_FRONT_WHEEL_SPEED_SENSOR as _RIGHT_FRONT_WHEEL_SPEED_SENSOR


@_controller(_MAIN_CONTROLLER)
class RaspberryPi4B(_Controller):
    def read(self) -> None:
        return None


@_device([_LEFT_FRONT_WHEEL_SPEED_SENSOR, _RIGHT_FRONT_WHEEL_SPEED_SENSOR], _MAIN_CONTROLLER)
class WheelSpeedSensor(_Device):
    def read(self) -> _Any:
        return None
