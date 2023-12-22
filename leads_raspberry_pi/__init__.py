from importlib.util import find_spec as _find_spec

if not _find_spec("serial"):
    raise ImportError("Please install `pyserial` to run this module\n>>>pip install pyserial")

from leads_raspberry_pi.raspberry_pi_4b import *
from leads_raspberry_pi.gps_receiver import *
