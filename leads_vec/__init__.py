from importlib.util import find_spec as _find_spec

if not _find_spec("pynput"):
    raise ImportError("Please install `pynput` to run this module\n>>>pip install pynput")

from leads_vec.run import *
from leads_vec.__entry__ import __entry__
from leads_vec.config import *
