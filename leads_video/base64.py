from base64 import b64encode as _b64encode
from io import BytesIO as _BytesIO
from typing import Literal as _Literal

from PIL.Image import Image as _Image, fromarray as _fromarray
from numpy import ndarray as _ndarray


def encode_image(x: _ndarray | None, mode: _Literal["L", "RGB"] | None = None) -> _Image | None:
    return None if x is None else _fromarray(x, mode)


def base64_encode(x: _ndarray | None, mode: _Literal["L", "RGB"] | None = None, quality: int = 25) -> str:
    if x is None:
        return ""
    _fromarray(x, mode).save(buffer := _BytesIO(), "JPEG", quality=quality)
    return _b64encode(buffer.getvalue()).decode()
