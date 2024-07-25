from typing import override

from leads import device, controller, MAIN_CONTROLLER, LEFT_FRONT_WHEEL_SPEED_SENSOR, RIGHT_FRONT_WHEEL_SPEED_SENSOR, \
    Controller, CENTER_REAR_WHEEL_SPEED_SENSOR, require_config, mark_device, ODOMETER, GPS_RECEIVER, \
    ConcurrentOdometer, LEFT_INDICATOR, RIGHT_INDICATOR, VOLTAGE_SENSOR, DataContainer, has_device, \
    FRONT_VIEW_CAMERA, LEFT_VIEW_CAMERA, RIGHT_VIEW_CAMERA, REAR_VIEW_CAMERA, VisualDataContainer, BRAKE_INDICATOR, \
    SFT, read_device_marker, has_controller
from leads_arduino import ArduinoMicro, WheelSpeedSensor, VoltageSensor
from leads_gpio import NMEAGPSReceiver, LEDGroup, LED, LEDGroupCommand, LEDCommand, Entire, Transition
from leads_gui import Config
from leads_video import Base64Camera, get_camera

config: Config = require_config()
GPS_ONLY: int = config.get("gps_only", False)
BAUD_RATE: int = config.get("baud_rate", 9600)
POWER_CONTROLLER_PORT: str = config.get("power_controller_port", "COM4")
WHEEL_SPEED_CONTROLLER_PORT: str = config.get("wheel_speed_controller_port", "COM3")
GPS_RECEIVER_PORT: str = config.get("gps_receiver_port", "COM5")
FRONT_WHEEL_DIAMETER: float = config.get("front_wheel_diameter", 20)  # 20 inches
REAR_WHEEL_DIAMETER: float = config.get("rear_wheel_diameter", 20)  # 20 inches
NUM_DIVISIONS: int = config.get("num_divisions", 1)
THROTTLE_PEDAL_PIN: int = config.get("throttle_pedal_pin", 2)
BRAKE_PEDAL_PIN: int = config.get("brake_pedal_pin", 3)
VOLTAGE_SENSOR_PIN: int = config.get("voltage_sensor_pin", 4)


@controller(MAIN_CONTROLLER)
class VeCController(Controller):
    @override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        if not has_controller("pc"):
            mark_device(self, "POWER", "BATT", "MOTOR", "BRAKE")
        if not has_controller("wsc"):
            mark_device(self, "WSC", "ESC")
        if not has_device(ODOMETER):
            mark_device(self, "WSC")
        if not has_device(GPS_RECEIVER):
            mark_device(self, "GPS")
        if not has_device(BRAKE_INDICATOR):
            mark_device(self, "LIGHT")
        if not has_device(LEFT_INDICATOR):
            mark_device(self, "LIGHT")
        if not has_device(RIGHT_INDICATOR):
            mark_device(self, "LIGHT")
        if read_device_marker(self):
            SFT.fail(self, RuntimeError("Unexpected system integrity"))

    @override
    def read(self) -> DataContainer:
        general = {
            "mileage": self.device(ODOMETER).read(),
            "gps_valid": (gps := self.device(GPS_RECEIVER).read())[0],
            "gps_ground_speed": gps[1],
            "latitude": gps[2],
            "longitude": gps[3],
            **self.device("pc").read()
        }
        wsc = {"speed": gps[0]} if GPS_ONLY else self.device("wsc").read()
        visual = {}
        if has_device(FRONT_VIEW_CAMERA):
            cam = get_camera(FRONT_VIEW_CAMERA, Base64Camera)
            visual["front_view_base64"] = cam.read()
            visual["front_view_latency"] = int(cam.latency() * 1000)
        if has_device(LEFT_VIEW_CAMERA):
            cam = get_camera(LEFT_VIEW_CAMERA, Base64Camera)
            visual["left_view_base64"] = cam.read()
            visual["left_view_latency"] = int(cam.latency() * 1000)
        if has_device(RIGHT_VIEW_CAMERA):
            cam = get_camera(RIGHT_VIEW_CAMERA, Base64Camera)
            visual["right_view_base64"] = cam.read()
            visual["right_view_latency"] = int(cam.latency() * 1000)
        if has_device(REAR_VIEW_CAMERA):
            cam = get_camera(REAR_VIEW_CAMERA, Base64Camera)
            visual["rear_view_base64"] = cam.read()
            visual["rear_view_latency"] = int(cam.latency() * 1000)
        return DataContainer(**wsc, **general) if len(visual) < 1 else VisualDataContainer(**visual, **wsc, **general)


@controller("pc", MAIN_CONTROLLER, (POWER_CONTROLLER_PORT, BAUD_RATE))
class PowerController(ArduinoMicro):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "POWER", "BATT", "MOTOR", "BRAKE")
        super().initialize(*parent_tags)

    @override
    def read(self) -> dict[str, float]:
        return {"voltage": self.device(VOLTAGE_SENSOR).read()}

    @override
    def write(self, payload: float) -> None:
        super().write(str(payload).encode())


@device(VOLTAGE_SENSOR, "pc")
class BatteryVoltageSensor(VoltageSensor):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "POWER", "BATT")
        super().initialize(*parent_tags)


@controller("wsc", MAIN_CONTROLLER, (WHEEL_SPEED_CONTROLLER_PORT, BAUD_RATE))
class WheelSpeedController(ArduinoMicro):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "WSC", "ESC")
        super().initialize(*parent_tags)

    @override
    def read(self) -> dict[str, float]:
        lfws = self.device(LEFT_FRONT_WHEEL_SPEED_SENSOR).read()
        rfws = self.device(RIGHT_FRONT_WHEEL_SPEED_SENSOR).read()
        front_wheel_speed = (lfws + rfws) * .5
        return {"speed": min(lfws, rfws, rws := self.device(CENTER_REAR_WHEEL_SPEED_SENSOR).read()),
                "front_wheel_speed": front_wheel_speed, "rear_wheel_speed": rws}


@device(ODOMETER, MAIN_CONTROLLER)
class AverageOdometer(ConcurrentOdometer):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "WSC")
        super().initialize(*parent_tags)

    @override
    def read(self) -> float:
        return super().read() / 3


@device(*(((LEFT_FRONT_WHEEL_SPEED_SENSOR, RIGHT_FRONT_WHEEL_SPEED_SENSOR, CENTER_REAR_WHEEL_SPEED_SENSOR), "wsc",
           [(FRONT_WHEEL_DIAMETER, NUM_DIVISIONS, ODOMETER), (FRONT_WHEEL_DIAMETER, NUM_DIVISIONS, ODOMETER),
            (REAR_WHEEL_DIAMETER, NUM_DIVISIONS, ODOMETER)])))
class WheelSpeedSensors(WheelSpeedSensor):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "WSC", "ESC")
        super().initialize(*parent_tags)


@device(GPS_RECEIVER, MAIN_CONTROLLER, (GPS_RECEIVER_PORT,))
class GPS(NMEAGPSReceiver):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "GPS")
        super().initialize(*parent_tags)


class Indicator(LEDGroup):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "LIGHT")
        super().initialize(*parent_tags)


@device(BRAKE_INDICATOR, MAIN_CONTROLLER, (LED(23), LED(24)))
class BrakeIndicator(Indicator):
    @override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        super().write(LEDGroupCommand(LEDCommand.BLINK_ONCE, Entire()))

    @override
    def write(self, payload: bool) -> None:
        super().write(LEDGroupCommand(
            LEDCommand.OFF, Entire()
        ) if payload else LEDGroupCommand(LEDCommand.OFF, Entire()))


@device(LEFT_INDICATOR, MAIN_CONTROLLER, (LED(5, .5, .5), LED(6, .5, .5), LED(26, .5, .5)))
class LeftIndicator(Indicator):
    @override
    def write(self, payload: bool) -> None:
        super().write(LEDGroupCommand(
            LEDCommand.BLINK, Transition("left2right", 100)
        ) if payload else LEDGroupCommand(LEDCommand.OFF, Entire()))


@device(RIGHT_INDICATOR, MAIN_CONTROLLER, (LED(17, .5, .5), LED(27, .5, .5), LED(22, .5, .5)))
class RightIndicator(Indicator):
    @override
    def write(self, payload: bool) -> None:
        super().write(LEDGroupCommand(
            LEDCommand.BLINK, Transition("right2left", 100)
        ) if payload else LEDGroupCommand(LEDCommand.OFF, Entire()))
