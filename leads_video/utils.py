from base64 import b64encode as _b64encode, b64decode as _b64decode
from io import BytesIO as _BytesIO
from typing import Literal as _Literal

from PIL.Image import Image as _Image, fromarray as _fromarray, open as _open, \
    UnidentifiedImageError as _UnidentifiedImageError
from numpy import ndarray as _ndarray, array as _array

from leads import has_device as _has_device, get_device as _get_device
from leads_video.camera import Camera


def encode_image(x: _ndarray | None, mode: _Literal["L", "RGB"] | None = None) -> _Image | None:
    return None if x is None else _fromarray(x.transpose(1, 2, 0), mode)


def base64_encode(x: _ndarray | None, mode: _Literal["L", "RGB"] | None = None, quality: int = 25) -> str:
    if not (img := encode_image(x, mode)):
        return ""
    img.save(buffer := _BytesIO(), "JPEG", quality=quality)
    return _b64encode(buffer.getvalue()).decode()


def base64_decode_image(x_base64: str) -> _Image | None:
    try:
        return _open(_BytesIO(_b64decode(x_base64))) if x_base64 else None
    except (ValueError, TypeError, _UnidentifiedImageError):
        return


def base64_decode(x_base64: str) -> _ndarray | None:
    return _array(image).transpose(2, 0, 1) if (image := base64_decode_image(x_base64)) else None


def get_camera(tag: str, required_type: type[Camera] = Camera) -> Camera | None:
    if not _has_device(tag):
        return None
    cam = _get_device(tag)
    if not isinstance(cam, required_type):
        raise TypeError(f"Device \"{tag}\" is supposed to be a camera")
    return cam
