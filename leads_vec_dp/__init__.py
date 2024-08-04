from importlib.util import find_spec as _find_spec

if not _find_spec("yaml"):
    raise ImportError("Please install `pyyaml` to run this module\n>>>pip install pyyaml")

from leads_vec_dp.__entry__ import __entry__
from leads_vec_dp.run import *
