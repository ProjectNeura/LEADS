from typing import Optional as _Optional

from leads import device, controller, MAIN_CONTROLLER, get_controller, WHEEL_SPEED_CONTROLLER, SRWDataContainer, \
    DRWDataContainer, LEFT_FRONT_WHEEL_SPEED_SENSOR, RIGHT_FRONT_WHEEL_SPEED_SENSOR, \
    CENTER_REAR_WHEEL_SPEED_SENSOR, LEFT_REAR_WHEEL_SPEED_SENSOR, RIGHT_REAR_WHEEL_SPEED_SENSOR, get_config, \
    mark_system, POWER_CONTROLLER
from leads_arduino import ArduinoMicro, WheelSpeedSensor, ArduinoCallback, VoltageSensor
from leads_gui import Config
from leads_raspberry_pi import RaspberryPi4B

config = get_config(Config)
BAUD_RATE: int = config.get("baud_rate", 9600)
POWER_CONTROLLER_PORT: str = config.get("power_controller_port", "COM4")
WHEEL_SPEED_CONTROLLER_PORT: str = config.get("wheel_speed_controller_port", "COM3")
FRONT_WHEEL_DIAMETER: float = config.get("front_wheel_diameter", 20)  # 20 inches
REAR_WHEEL_DIAMETER: float = config.get("rear_wheel_diameter", 20)  # 20 inches
THROTTLE_PEDAL_PIN: int = config.get("throttle_pedal_pin", 2)
BRAKE_PEDAL_PIN: int = config.get("brake_pedal_pin", 3)
VOLTAGE_SENSOR_PIN: int = config.get("voltage_sensor_pin", 4)


@controller(MAIN_CONTROLLER)
class VeCController(RaspberryPi4B):
    def read(self) -> SRWDataContainer | DRWDataContainer:
        r = get_controller(WHEEL_SPEED_CONTROLLER).read()
        return SRWDataContainer(*r) if config.srw_mode else DRWDataContainer(*r)


@controller(POWER_CONTROLLER, MAIN_CONTROLLER, (POWER_CONTROLLER_PORT, ArduinoCallback(POWER_CONTROLLER), BAUD_RATE))
class PowerController(ArduinoMicro):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "PC")
        super().initialize(*parent_tags)

    def read(self) -> float:
        return self.device("vot").read()


@device("vot", POWER_CONTROLLER)
class BatteryVoltageSensor(VoltageSensor):
    pass


@controller(WHEEL_SPEED_CONTROLLER, MAIN_CONTROLLER, (
        WHEEL_SPEED_CONTROLLER_PORT, ArduinoCallback(WHEEL_SPEED_CONTROLLER), BAUD_RATE
))
class WheelSpeedController(ArduinoMicro):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "WSC", "ECS")
        super().initialize(*parent_tags)

    def read(self) -> [float, float, float, _Optional[float]]:
        lfws = self.device(LEFT_FRONT_WHEEL_SPEED_SENSOR).read()
        rfws = self.device(RIGHT_FRONT_WHEEL_SPEED_SENSOR).read()
        rws = (self.device(CENTER_REAR_WHEEL_SPEED_SENSOR).read(),) if config.srw_mode else (
            self.device(LEFT_REAR_WHEEL_SPEED_SENSOR).read(),
            self.device(RIGHT_REAR_WHEEL_SPEED_SENSOR).read()
        )
        return min(lfws, rfws, *rws), (lfws + rfws) * .5, *rws


@device(*((
        (LEFT_FRONT_WHEEL_SPEED_SENSOR,
         RIGHT_FRONT_WHEEL_SPEED_SENSOR,
         CENTER_REAR_WHEEL_SPEED_SENSOR),
        WHEEL_SPEED_CONTROLLER,
        [(FRONT_WHEEL_DIAMETER,),
         (FRONT_WHEEL_DIAMETER,),
         (REAR_WHEEL_DIAMETER,)
         ]) if config.srw_mode else (
        (LEFT_FRONT_WHEEL_SPEED_SENSOR,
         RIGHT_FRONT_WHEEL_SPEED_SENSOR,
         LEFT_REAR_WHEEL_SPEED_SENSOR,
         RIGHT_REAR_WHEEL_SPEED_SENSOR),
        WHEEL_SPEED_CONTROLLER,
        [(FRONT_WHEEL_DIAMETER,),
         (FRONT_WHEEL_DIAMETER,),
         (REAR_WHEEL_DIAMETER,),
         (REAR_WHEEL_DIAMETER,)]
)))
class WheelSpeedSensors(WheelSpeedSensor):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "WSC", "ECS")
        super().initialize(*parent_tags)


# @device((THROTTLE_PEDAL, BRAKE_PEDAL), MAIN_CONTROLLER, [(THROTTLE_PEDAL_PIN, False), (BRAKE_PEDAL_PIN, True)])
# class Pedals(Pedal):
#     def __init__(self, pin: int, brake: bool) -> None:
#         super().__init__(pin)
#         self._brake: bool = brake


_ = None  # null export
