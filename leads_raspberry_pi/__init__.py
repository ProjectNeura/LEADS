from importlib.util import find_spec as _find_spec

if not _find_spec("gpiozero"):
    raise ImportError("Please install `gpiozero` to run this module\n>>>pip install gpiozero")
if not _find_spec("pynmea2"):
    raise ImportError("Please install `pynmea2` to run this module\n>>>pip install pynmea2")
if not _find_spec("serial"):
    raise ImportError("Please install `pyserial` to run this module\n>>>pip install pyserial")

from leads_raspberry_pi.gps_receiver import *
from leads_raspberry_pi.led import *
from leads_raspberry_pi.led_group import *
