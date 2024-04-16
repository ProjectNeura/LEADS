from leads import device, controller, MAIN_CONTROLLER, LEFT_FRONT_WHEEL_SPEED_SENSOR, RIGHT_FRONT_WHEEL_SPEED_SENSOR, \
    Controller, CENTER_REAR_WHEEL_SPEED_SENSOR, require_config, mark_system, ODOMETER, GPS_RECEIVER, \
    ConcurrentOdometer, LEFT_INDICATOR, RIGHT_INDICATOR, VOLTAGE_SENSOR, DataContainer
from leads_arduino import ArduinoMicro, WheelSpeedSensor, VoltageSensor
from leads_raspberry_pi import NMEAGPSReceiver, LEDGroup, LED, LEDGroupCommand, LEDCommand, Entire

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
    def read(self) -> DataContainer:
        universal = {
            "mileage": self.device(ODOMETER).read(),
            "gps_valid": (coords := self.device(GPS_RECEIVER).read())[0],
            "gps_ground_speed": coords[1],
            "latitude": coords[2],
            "longitude": coords[3],
            **self.device("pc").read()
        }
        return DataContainer(**self.device("wsc").read(), **universal)


@controller("pc", MAIN_CONTROLLER, (POWER_CONTROLLER_PORT, BAUD_RATE))
class PowerController(ArduinoMicro):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "POWER", "BATT", "MOTOR")
        super().initialize(*parent_tags)

    def read(self) -> dict[str, float]:
        return {"voltage": self.device(VOLTAGE_SENSOR).read()}

    def write(self, payload: float) -> None:
        super().write(str(payload).encode())


@device(VOLTAGE_SENSOR, "pc")
class BatteryVoltageSensor(VoltageSensor):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "POWER", "BATT")
        super().initialize(*parent_tags)


@controller("wsc", MAIN_CONTROLLER, (WHEEL_SPEED_CONTROLLER_PORT, BAUD_RATE))
class WheelSpeedController(ArduinoMicro):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "WSC", "ESC")
        super().initialize(*parent_tags)

    def read(self) -> dict[str, float]:
        lfws = self.device(LEFT_FRONT_WHEEL_SPEED_SENSOR).read()
        rfws = self.device(RIGHT_FRONT_WHEEL_SPEED_SENSOR).read()
        front_wheel_speed = (lfws + rfws) * .5
        return {"speed": min(lfws, rfws, rws := self.device(CENTER_REAR_WHEEL_SPEED_SENSOR).read()),
                "front_wheel_speed": front_wheel_speed, "rear_wheel_speed": rws}


@device(ODOMETER, MAIN_CONTROLLER)
class AverageOdometer(ConcurrentOdometer):
    def read(self) -> float:
        return super().read() / 3


@device(*(((LEFT_FRONT_WHEEL_SPEED_SENSOR, RIGHT_FRONT_WHEEL_SPEED_SENSOR, CENTER_REAR_WHEEL_SPEED_SENSOR), "wsc",
           [(FRONT_WHEEL_DIAMETER, ODOMETER), (FRONT_WHEEL_DIAMETER, ODOMETER), (REAR_WHEEL_DIAMETER, ODOMETER)])))
class WheelSpeedSensors(WheelSpeedSensor):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "WSC", "ESC")
        super().initialize(*parent_tags)


@device(GPS_RECEIVER, MAIN_CONTROLLER, (GPS_RECEIVER_PORT,))
class GPS(NMEAGPSReceiver):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "GPS")
        super().initialize(*parent_tags)


@device((LEFT_INDICATOR, RIGHT_INDICATOR), MAIN_CONTROLLER, [
    (LED(5, .5, .5), LED(6, .5, .5), LED(26, .5, .5)), (LED(17, .5, .5), LED(27, .5, .5), LED(22, .5, .5))
])
class DirectionIndicators(LEDGroup):
    def initialize(self, *parent_tags: str) -> None:
        mark_system(self, "DI")
        super().initialize(*parent_tags)
        self.write(LEDGroupCommand(LEDCommand.BLINK_ONCE, Entire()))
