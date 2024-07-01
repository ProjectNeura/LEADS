from base64 import b64encode as _b64encode
from io import BytesIO as _BytesIO
from typing import Literal as _Literal

from PIL.Image import fromarray as _fromarray
from numpy import ndarray as _ndarray


def base64_encode(x: _ndarray, mode: _Literal["L", "RGB"] | None = None) -> str:
    img = _fromarray(x, mode)
    buffer = _BytesIO()
    img.save(buffer, "PNG")
    return _b64encode(buffer.getvalue()).decode()
