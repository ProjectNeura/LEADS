from importlib.util import find_spec as _find_spec

if not _find_spec("cv2"):
    raise ImportError("Please install `opencv-python-headless` to run this module\n>>>pip install opencv-python")
if not _find_spec("PIL"):
    raise ImportError("Please install `Pillow` to run this module\n>>>pip install Pillow")

from leads_video.base64 import *
from leads_video.camera import *
from leads_video.utils import *
