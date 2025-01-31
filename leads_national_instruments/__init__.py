from importlib.util import find_spec as _find_spec

if not _find_spec("nidaqmx"):
    raise ImportError("Please install `nidaqmx` to run this module\n>>>pip install nidaqmx")

from leads_gui.system import get_system_kernel as _get_system_kernel

if _get_system_kernel() not in ("windows", "linux"):
    raise ImportError("National Instruments bindings for Python only supports Windows environments")

from leads_national_instruments.mydaq import *
