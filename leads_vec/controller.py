from leads import device, controller, MAIN_CONTROLLER, get_controller, WHEEL_SPEED_CONTROLLER, SRWDataContainer, \
    DRWDataContainer, LEFT_FRONT_WHEEL_SPEED_SENSOR, RIGHT_FRONT_WHEEL_SPEED_SENSOR, Controller, \
    CENTER_REAR_WHEEL_SPEED_SENSOR, LEFT_REAR_WHEEL_SPEED_SENSOR, RIGHT_REAR_WHEEL_SPEED_SENSOR, get_config, \
    mark_system, POWER_CONTROLLER, ODOMETER, GPS_RECEIVER
from leads_arduino import ArduinoMicro, WheelSpeedSensor, ArduinoCallback, VoltageSensor, ConcurrentOdometer
from leads_gui import Config
from leads_raspberry_pi import GPSReceiver

config = get_config(Config)
BAUD_RATE: int = config.get("baud_rate", 9600)
POWER_CONTROLLER_PORT: str = config.get("power_controller_port", "COM4")
WHEEL_SPEED_CONTROLLER_PORT: str = config.get("wheel_speed_controller_port", "COM3")
GPS_RECEIVER_PORT: str = config.get("gps_receiver_port", "COM5")
FRONT_WHEEL_DIAMETER: float = config.get("front_wheel_diameter", 20)  # 20 inches
REAR_WHEEL_DIAMETER: float = config.get("rear_wheel_diameter", 20)  # 20 inches
THROTTLE_PEDAL_PIN: int = config.get("throttle_pedal_pin", 2)
BRAKE_PEDAL_PIN: int = config.get("brake_pedal_pin", 3)
VOLTAGE_SENSOR_PIN: int = config.get("voltage_sensor_pin", 4)


@controller(MAIN_CONTROLLER)
class VeCController(Controller):
    def read(self) -> SRWDataContainer | DRWDataContainer:
        r = get_controller(WHEEL_SPEED_CONTROLLER).read()
        universal = {
            "voltage": get_controller(POWER_CONTROLLER).read(),
            "mileage": self.device(ODOMETER).read(),
            "gps_valid": (coords := self.device(GPS_RECEIVER).read())[0],
            "latitude": coords[1],
            "longitude": coords[2]
        }
        return SRWDataContainer(**r, **universal) if config.srw_mode else DRWDataContainer(**r, **universal)


@controller(POWER_CONTROLLER, MAIN_CONTROLLER, (POWER_CONTROLLER_PORT, ArduinoCallback(POWER_CONTROLLER), BAUD_RATE))
class PowerController(ArduinoMicro):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "POWER", "BATT", "MOTOR")
        super().initialize(*parent_tags)

    def read(self) -> float:
        return self.device("vot").read()


@device("vot", POWER_CONTROLLER)
class BatteryVoltageSensor(VoltageSensor):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "POWER", "BATT")


@controller(WHEEL_SPEED_CONTROLLER, MAIN_CONTROLLER, (
        WHEEL_SPEED_CONTROLLER_PORT, ArduinoCallback(WHEEL_SPEED_CONTROLLER), BAUD_RATE
))
class WheelSpeedController(ArduinoMicro):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "WSC", "ECS")
        super().initialize(*parent_tags)

    def read(self) -> dict[str, float]:
        lfws = self.device(LEFT_FRONT_WHEEL_SPEED_SENSOR).read()
        rfws = self.device(RIGHT_FRONT_WHEEL_SPEED_SENSOR).read()
        front_wheel_speed = (lfws + rfws) * .5
        return {
            "min_speed": min(lfws, rfws, rws := self.device(CENTER_REAR_WHEEL_SPEED_SENSOR).read()),
            "front_wheel_speed": front_wheel_speed,
            "rear_wheel_speed": rws
        } if config.srw_mode else {
            "min_speed": min(lfws, rfws, lrws := self.device(LEFT_REAR_WHEEL_SPEED_SENSOR).read(),
                             rrws := self.device(RIGHT_REAR_WHEEL_SPEED_SENSOR).read()),
            "front_wheel_speed": front_wheel_speed,
            "left_rear_wheel_speed": lrws,
            "right_rear_wheel_speed": rrws
        }


@device(ODOMETER, MAIN_CONTROLLER)
class AverageOdometer(ConcurrentOdometer):
    def read(self) -> float:
        return super().read() / (3 if config.srw_mode else 4)


@device(*((
        (LEFT_FRONT_WHEEL_SPEED_SENSOR,
         RIGHT_FRONT_WHEEL_SPEED_SENSOR,
         CENTER_REAR_WHEEL_SPEED_SENSOR),
        WHEEL_SPEED_CONTROLLER,
        [(FRONT_WHEEL_DIAMETER, ODOMETER),
         (FRONT_WHEEL_DIAMETER, ODOMETER),
         (REAR_WHEEL_DIAMETER, ODOMETER)
         ]) if config.srw_mode else (
        (LEFT_FRONT_WHEEL_SPEED_SENSOR,
         RIGHT_FRONT_WHEEL_SPEED_SENSOR,
         LEFT_REAR_WHEEL_SPEED_SENSOR,
         RIGHT_REAR_WHEEL_SPEED_SENSOR),
        WHEEL_SPEED_CONTROLLER,
        [(FRONT_WHEEL_DIAMETER, ODOMETER),
         (FRONT_WHEEL_DIAMETER, ODOMETER),
         (REAR_WHEEL_DIAMETER, ODOMETER),
         (REAR_WHEEL_DIAMETER, ODOMETER)]
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


@device(GPS_RECEIVER, MAIN_CONTROLLER, (GPS_RECEIVER_PORT,))
class GPS(GPSReceiver):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "GPS")
        super().initialize(*parent_tags)


_ = None  # null export
