from leads import L, controller, MAIN_CONTROLLER, get_controller, WHEEL_SPEED_CONTROLLER, SRWDataContainer
from leads.comm import Callback, Service, ConnectionBase
from leads_arduino import ArduinoMicro
from leads_emulation import SRWRandom

# FixMe
"""
These parameters should somehow be loaded from the config
But the config file currently has no way to be passed into this module
"""
WHEEL_RADIUS: float = 159.5  # 20 inches


@controller(MAIN_CONTROLLER)
class VeCController(SRWRandom):
    def read(self) -> SRWDataContainer:
        return SRWDataContainer(*get_controller(WHEEL_SPEED_CONTROLLER).read())


class WheelSpeedControllerCallback(Callback):
    def on_connect(self, service: Service, connection: ConnectionBase) -> None:
        L.debug("Wheel speed controller connected")

    def on_receive(self, service: Service, msg: bytes) -> None:
        get_controller(WHEEL_SPEED_CONTROLLER).update(float(msg.decode()))

    def on_fail(self, service: Service, error: Exception) -> None:
        L.error(str(error))


@controller(WHEEL_SPEED_CONTROLLER, MAIN_CONTROLLER, ("COM6", WheelSpeedControllerCallback()))
class WheelSpeedController(ArduinoMicro):
    _wheel_speed: float = 0

    def update(self, data: float) -> None:
        self._wheel_speed = data * WHEEL_RADIUS * .0006

    def read(self) -> [float, float]:
        return self._wheel_speed, self._wheel_speed


_ = None  # null export
