from leads import L, controller, MAIN_CONTROLLER, get_controller, WHEEL_SPEED_CONTROLLER, SRWDataContainer
from leads.config import get_config
from leads_gui import Config
from leads.comm import Callback, Service, ConnectionBase
from leads_arduino import ArduinoMicro
from leads_emulation import SRWRandom

config = get_config(Config)
WHEEL_SPEED_CONTROLLER_PORT: str = config.get("wheel_speed_controller_port", "COM3")
WHEEL_RADIUS: float = config.get("wheel_radius", 159.5)  # 20 inches


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


@controller(WHEEL_SPEED_CONTROLLER, MAIN_CONTROLLER, (WHEEL_SPEED_CONTROLLER_PORT, WheelSpeedControllerCallback()))
class WheelSpeedController(ArduinoMicro):
    _wheel_speed: float = 0

    def update(self, data: float) -> None:
        self._wheel_speed = data * WHEEL_RADIUS * .0006

    def read(self) -> [float, float]:
        return self._wheel_speed, self._wheel_speed


_ = None  # null export
