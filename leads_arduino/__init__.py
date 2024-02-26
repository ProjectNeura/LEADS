from importlib.util import find_spec as _find_spec

if not _find_spec("serial"):
    raise ImportError("Please install `pyserial` to run this module\n>>>pip install pyserial")

from leads_arduino.arduino_proto import *
from leads_arduino.arduino_nano import *
from leads_arduino.arduino_micro import *
from leads_arduino.voltage_sensor import *
from leads_arduino.wheel_speed_sensor import *
