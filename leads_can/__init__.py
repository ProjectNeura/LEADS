from importlib.util import find_spec as _find_spec

if not _find_spec("can"):
    raise ImportError("Please install `python-can` to run this module\n>>>pip install python-can")

from leads_can.prototype import *
from leads_can.obd import *
