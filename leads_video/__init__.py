from importlib.util import find_spec as _find_spec

if not _find_spec("cv2"):
    raise ImportError("Please install `opencv-python` to run this module\n>>>pip install opencv-python")

from leads_video.camera import *
