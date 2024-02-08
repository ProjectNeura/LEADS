from leads import L, device, controller, MAIN_CONTROLLER, get_controller, WHEEL_SPEED_CONTROLLER, THROTTLE_PEDAL, \
    SRWDataContainer, DRWDataContainer, BRAKE_PEDAL, DC_MOTOR_CONTROLLER_A
from leads.config import get_config
from leads_gui import Config
from leads.comm import Callback, Service, ConnectionBase
from leads_arduino import ArduinoMicro
from leads_raspberry_pi import RaspberryPi4B, Pedal, DCMotorController

config = get_config(Config)
BAUD_RATE: int = config.get("baud_rate", 9600)
WHEEL_SPEED_CONTROLLER_PORT: str = config.get("wheel_speed_controller_port", "COM3")
WHEEL_RADIUS: float = config.get("wheel_radius", 159.5)  # 20 inches
THROTTLE_PEDAL_PIN: int = config.get("throttle_pedal_pin", 2)
BRAKE_PEDAL_PIN: int = config.get("brake_pedal_pin", 3)


@controller(MAIN_CONTROLLER)
class VeCController(RaspberryPi4B):
    def read(self) -> SRWDataContainer | DRWDataContainer:
        return SRWDataContainer(
            *get_controller(WHEEL_SPEED_CONTROLLER).read()
        ) if config.srw_mode else DRWDataContainer(
            *get_controller(WHEEL_SPEED_CONTROLLER).read()
        )


class WheelSpeedControllerCallback(Callback):
    def on_connect(self, service: Service, connection: ConnectionBase) -> None:
        L.debug("Wheel speed controller connected")

    def on_receive(self, service: Service, msg: bytes) -> None:
        get_controller(WHEEL_SPEED_CONTROLLER).update(float(msg.decode()))

    def on_fail(self, service: Service, error: Exception) -> None:
        L.error(str(error))


@controller(WHEEL_SPEED_CONTROLLER, MAIN_CONTROLLER, (
        WHEEL_SPEED_CONTROLLER_PORT, WheelSpeedControllerCallback(), BAUD_RATE
))
class WheelSpeedController(ArduinoMicro):
    _wheel_speed: float = 0

    def update(self, data: float) -> None:
        self._wheel_speed = data * WHEEL_RADIUS * .0006

    def read(self) -> [float, float]:
        return self._wheel_speed, self._wheel_speed


@device((THROTTLE_PEDAL, BRAKE_PEDAL), MAIN_CONTROLLER, [(THROTTLE_PEDAL_PIN, False), (BRAKE_PEDAL_PIN, True)])
class Pedals(Pedal):
    def __init__(self, pin: int, brake: bool) -> None:
        super().__init__(pin)
        self._brake: bool = brake


@device(DC_MOTOR_CONTROLLER_A, MAIN_CONTROLLER)
class DriverMotorController(DCMotorController):
    pass


_ = None  # null export
