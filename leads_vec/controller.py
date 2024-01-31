from leads import *
from leads_arduino import *
from leads_raspberry_pi import *


@controller(MAIN_CONTROLLER)
class VeCController(RaspberryPi4B):
    pass


@controller(WHEEL_SPEED_CONTROLLER, MAIN_CONTROLLER)
class WheelSpeedSubsystem(ArduinoMicro):
    pass


@device(LEFT_FRONT_WHEEL_SPEED_SENSOR, WHEEL_SPEED_CONTROLLER)
class LeftFrontWheelSpeedSensor(WheelSpeedSensor):
    pass


_ = None    # null export
