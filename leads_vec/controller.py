from leads import *
from leads_arduino import *
from leads_raspberry_pi import *


@controller(MAIN_CONTROLLER)
class VeCController(RaspberryPi4B):
    pass


@device(WHEEL_SPEED_SUBSYSTEM, MAIN_CONTROLLER)
class WheelSpeedSubsystem(ArduinoMicro):
    pass


_ = None    # null export
