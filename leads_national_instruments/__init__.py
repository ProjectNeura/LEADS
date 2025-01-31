from importlib.util import find_spec as _find_spec

if not _find_spec("nidaqmx"):
    raise ImportError("Please install `nidaqmx` to run this module\n>>>pip install nidaqmx")

from leads_national_instruments.mydaq import *
