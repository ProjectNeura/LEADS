from typing import override

from leads import device, controller, MAIN_CONTROLLER, LEFT_FRONT_WHEEL_SPEED_SENSOR, RIGHT_FRONT_WHEEL_SPEED_SENSOR, \
    Controller, CENTER_REAR_WHEEL_SPEED_SENSOR, require_config, mark_device, ODOMETER, GPS_RECEIVER, \
    ConcurrentOdometer, LEFT_INDICATOR, RIGHT_INDICATOR, VOLTAGE_SENSOR, DataContainer, has_device, \
    FRONT_VIEW_CAMERA, LEFT_VIEW_CAMERA, RIGHT_VIEW_CAMERA, REAR_VIEW_CAMERA, VisualDataContainer, BRAKE_INDICATOR, \
    SFT, read_device_marker, has_controller, POWER_CONTROLLER, WHEEL_SPEED_CONTROLLER, ACCELEROMETER, require_context, \
    ltm_get, ltm_set, distance_between
from leads_arduino import ArduinoMicro, WheelSpeedSensor, VoltageSensor, Accelerometer, Acceleration
from leads_comm_serial import SOBD
from leads_gpio import NMEAGPSReceiver, LEDGroup, LED, LEDGroupCommand, LEDCommand, Entire, Transition, Button, \
    ButtonCallback, CPUMonitor
from leads_vec.config import Config
from leads_video import Base64Camera, get_camera

config: Config = require_config()
GPS_ONLY: int = config.get("gps_only", False)
BAUD_RATE: int = config.get("baud_rate", 9600)
SOBD_PORT: int = config.get("sobd_port", "auto")
SOBD_PASSWORD: int = config.get("sobd_password", "")
POWER_CONTROLLER_PORT: str = config.get("power_controller_port", "auto")
WHEEL_SPEED_CONTROLLER_PORT: str = config.get("wheel_speed_controller_port", "auto")
GPS_RECEIVER_PORT: str = config.get("gps_receiver_port", "auto")
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
        mark_device(self, "", append=False)
        if not has_controller(POWER_CONTROLLER):
            mark_device(self, "POWER", "BATT", "MOTOR", "BRAKE")
        if not has_controller(WHEEL_SPEED_CONTROLLER):
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
            "gps_valid": (gps := self.device(GPS_RECEIVER).read())[0],
            "gps_ground_speed": gps[1],
            "latitude": gps[2],
            "longitude": gps[3],
            **self.device(POWER_CONTROLLER).read()
        }
        wsc = self.device(WHEEL_SPEED_CONTROLLER).read()
        odometer = self.device(ODOMETER)
        if GPS_ONLY:
            wsc["speed"] = gps[1]
            prev = require_context().data()
            odometer.write(odometer.read() + distance_between(prev.latitude, prev.longitude, gps[2], gps[3]))
        general["mileage"] = odometer.read()
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


@device("obd", MAIN_CONTROLLER, (SOBD_PORT, BAUD_RATE, SOBD_PASSWORD))
class OBD(SOBD):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "OBD")
        super().initialize(*parent_tags)


@controller(POWER_CONTROLLER, MAIN_CONTROLLER, (POWER_CONTROLLER_PORT, BAUD_RATE))
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


@device(VOLTAGE_SENSOR, POWER_CONTROLLER)
class BatteryVoltageSensor(VoltageSensor):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "POWER", "BATT")
        super().initialize(*parent_tags)


@controller(WHEEL_SPEED_CONTROLLER, MAIN_CONTROLLER, (WHEEL_SPEED_CONTROLLER_PORT, BAUD_RATE))
class WheelSpeedController(ArduinoMicro):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "WSC", "ESC")
        super().initialize(*parent_tags)

    @override
    def read(self) -> dict[str, float]:
        lfws = self.device(LEFT_FRONT_WHEEL_SPEED_SENSOR).read()
        rfws = self.device(RIGHT_FRONT_WHEEL_SPEED_SENSOR).read()
        return {"speed": min(lfws, rfws, rws := self.device(CENTER_REAR_WHEEL_SPEED_SENSOR).read()),
                "front_wheel_speed": (lfws + rfws) * .5, "rear_wheel_speed": rws,
                **self.device(ACCELEROMETER).read().to_dict()}


@device(ODOMETER, MAIN_CONTROLLER)
class AverageOdometer(ConcurrentOdometer):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "WSC")
        super().initialize(*parent_tags)
        if config.use_ltm:
            self.write(ltm_get("mileage"))

    @override
    def write(self, payload: float) -> None:
        super().write(payload)
        ltm_set("mileage", payload)

    @override
    def read(self) -> float:
        return super().read() if GPS_ONLY else super().read() / 3


@device(*(((LEFT_FRONT_WHEEL_SPEED_SENSOR, RIGHT_FRONT_WHEEL_SPEED_SENSOR, CENTER_REAR_WHEEL_SPEED_SENSOR),
           WHEEL_SPEED_CONTROLLER,
           [(FRONT_WHEEL_DIAMETER, NUM_DIVISIONS, ODOMETER), (FRONT_WHEEL_DIAMETER, NUM_DIVISIONS, ODOMETER),
            (REAR_WHEEL_DIAMETER, NUM_DIVISIONS, ODOMETER)])))
class WheelSpeedSensors(WheelSpeedSensor):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "WSC", "ESC")
        super().initialize(*parent_tags)


@device(ACCELEROMETER, WHEEL_SPEED_CONTROLLER)
class LinearAccelerometer(Accelerometer):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "WSC", "ESC")
        super().initialize(*parent_tags)

    @override
    def read(self) -> Acceleration:
        return super().read().linear()


@device(GPS_RECEIVER, MAIN_CONTROLLER, (GPS_RECEIVER_PORT,))
class GPS(NMEAGPSReceiver):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "GPS")
        super().initialize(*parent_tags)


@device("cpu", MAIN_CONTROLLER)
class CPU(CPUMonitor):
    pass


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


@device("lib", MAIN_CONTROLLER, (16,))
class LeftIndicatorButton(Button, ButtonCallback):
    @override
    def on_pressed(self) -> None:
        ctx = require_context()
        ctx.left_indicator(not ctx.left_indicator())

    @override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self.write(self)


@device("rib", MAIN_CONTROLLER, (20,))
class RightIndicatorButton(Button, ButtonCallback):
    @override
    def on_pressed(self) -> None:
        ctx = require_context()
        ctx.right_indicator(not ctx.right_indicator())

    @override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self.write(self)


_: None = None
