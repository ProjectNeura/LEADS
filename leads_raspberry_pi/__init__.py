from importlib.util import find_spec as _find_spec

if not _find_spec("RPi"):
    raise ImportError("Please install `RPi.GPIO` to run this module\n>>>apt install python3-rpi.gpio")
if not _find_spec("pynmea2"):
    raise ImportError("Please install `pynmea2` to run this module\n>>>pip install pynmea2")
if not _find_spec("serial"):
    raise ImportError("Please install `pyserial` to run this module\n>>>pip install pyserial")

from leads_raspberry_pi.gps_receiver import *
from leads_raspberry_pi.dc_motor import *
