from importlib.util import find_spec as _find_spec

if not _find_spec("keyboard"):
    raise ImportError("Please install `keyboard` to run this module\n>>>pip install keyboard")
