from importlib.util import find_spec as _find_spec

if not _find_spec("sdl2"):
    raise ImportError("Please install `PySDL2` to run this module\n>>>pip install PySDL2")

from leads_audio.prototype import *
