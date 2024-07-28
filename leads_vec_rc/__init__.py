from importlib.util import find_spec as _find_spec

if not _find_spec("fastapi"):
    raise ImportError("Please install `fastapi` to run this module\n>>>pip install \"fastapi[standard]\"")
if not _find_spec("uvicorn"):
    raise ImportError("Please install `uvicorn` to run this module\n>>>pip install \"fastapi[standard]\"")

from leads_vec_rc.__entry__ import __entry__
