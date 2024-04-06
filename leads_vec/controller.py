from leads import device, controller, MAIN_CONTROLLER, get_controller, WHEEL_SPEED_CONTROLLER, SRWDataContainer, \
    DRWDataContainer, LEFT_FRONT_WHEEL_SPEED_SENSOR, RIGHT_FRONT_WHEEL_SPEED_SENSOR, Controller, \
    CENTER_REAR_WHEEL_SPEED_SENSOR, LEFT_REAR_WHEEL_SPEED_SENSOR, RIGHT_REAR_WHEEL_SPEED_SENSOR, require_config, \
    mark_system, POWER_CONTROLLER, ODOMETER, GPS_RECEIVER, ConcurrentOdometer
from leads_arduino import ArduinoMicro, WheelSpeedSensor, VoltageSensor
from leads_raspberry_pi import NMEAGPSReceiver, LEDGroup, LED, LEDGroupCommand, LEDCommand, Transition

config = require_config()
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
        universal = {
            "mileage": self.device(ODOMETER).read(),
            "gps_valid": (coords := self.device(GPS_RECEIVER).read())[0],
            "gps_ground_speed": coords[1],
            "latitude": coords[2],
            "longitude": coords[3],
            **get_controller(POWER_CONTROLLER).read()
        }
        return (SRWDataContainer if config.srw_mode else DRWDataContainer)(
            **get_controller(WHEEL_SPEED_CONTROLLER).read(), **universal)


@controller(POWER_CONTROLLER, MAIN_CONTROLLER, (POWER_CONTROLLER_PORT, BAUD_RATE))
class PowerController(ArduinoMicro):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "POWER", "BATT", "MOTOR")
        super().initialize(*parent_tags)

    def read(self) -> dict[str, float]:
        return {"voltage": self.device("vot").read()}

    def write(self, payload: float) -> None:
        super().write(str(payload).encode())


@device("vot", POWER_CONTROLLER)
class BatteryVoltageSensor(VoltageSensor):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "POWER", "BATT")


@controller(WHEEL_SPEED_CONTROLLER, MAIN_CONTROLLER, (WHEEL_SPEED_CONTROLLER_PORT, BAUD_RATE))
class WheelSpeedController(ArduinoMicro):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "WSC", "ESC")
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
        mark_system(self, "WSC", "ESC")
        super().initialize(*parent_tags)


@device(GPS_RECEIVER, MAIN_CONTROLLER, (GPS_RECEIVER_PORT,))
class GPS(NMEAGPSReceiver):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "GPS")
        super().initialize(*parent_tags)


@device("left_turning_light", MAIN_CONTROLLER, (LED(5), LED(6)))
class LeftTurningLight(LEDGroup):
    def initialize(self, *parent_tags: str) -> None:
        self.write(LEDGroupCommand(LEDCommand.BLINK, Transition("left2right")))


@device("right_turning_light", MAIN_CONTROLLER, (LED(17), LED(18)))
class RightTurningLight(LEDGroup):
    def initialize(self, *parent_tags: str) -> None:
        self.write(LEDGroupCommand(LEDCommand.BLINK, Transition("right2left")))


_ = None  # null export
