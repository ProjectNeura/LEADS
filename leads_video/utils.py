from base64 import b64encode as _b64encode, b64decode as _b64decode
from io import BytesIO as _BytesIO
from typing import Literal as _Literal

from PIL.Image import Image as _Image, fromarray as _fromarray, open as _open
from numpy import ndarray as _ndarray, array as _array


def base64_encode(x: _ndarray, mode: _Literal["L", "RGB"] | None = None) -> str:
    img = _fromarray(x, mode)
    buffer = _BytesIO()
    img.save(buffer, "PNG")
    return _b64encode(buffer.getvalue()).decode()


def base64_decode_image(x_base64: str) -> _Image:
    return _open(_BytesIO(_b64decode(x_base64)))


def base64_decode(x_base64: str) -> _ndarray:
    return _array(base64_decode_image(x_base64))
