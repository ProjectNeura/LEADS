from base64 import b64decode as _b64decode
from binascii import Error as _BinasciiError
from io import BytesIO as _BytesIO
from typing import Any as _Any, Literal as _Literal

from PIL.Image import Image as _Image, open as _open, UnidentifiedImageError as _UnidentifiedImageError
from cv2 import VideoWriter as _VideoWriter, VideoWriter_fourcc as _VideoWriter_fourcc, cvtColor as _cvtColor, \
    COLOR_RGB2BGR as _COLOR_RGB2BGR
from numpy import array as _array

from leads import has_device as _has_device, get_device as _get_device
from leads.data_persistence import CSVDataset as _CSVDataset
from leads_video.camera import Camera


def get_camera(tag: str, required_type: type[Camera] = Camera) -> Camera | None:
    if not _has_device(tag):
        return
    cam = _get_device(tag)
    if not isinstance(cam, required_type):
        raise TypeError(f"Device \"{tag}\" is supposed to be a camera")
    return cam


def _decode_frame(row: dict[str, _Any], tag: str) -> _Image:
    if not (frame := row[tag]):
        raise ValueError
    return _open(_BytesIO(_b64decode(frame)))


def extract_video(dataset: _CSVDataset, file: str, channel: _Literal["front", "left", "right", "rear"]) -> None:
    if not file.endswith(".mp4"):
        file += ".mp4"
    channel = f"{channel}_view_base64"
    prev_row = None
    resolution = None
    fps = 0
    cache = None
    for row in dataset:
        if not resolution:
            try:
                frame = _decode_frame(row, channel)
                cache = _cvtColor(_array(frame), _COLOR_RGB2BGR)
                resolution = _decode_frame(row, channel).size
            except (ValueError, _BinasciiError, _UnidentifiedImageError):
                pass
        if prev_row:
            local_fps = 1000 / (row["t"] - prev_row["t"])
            if local_fps > fps:
                fps = local_fps
        prev_row = row
    if not resolution or not fps or cache is None:
        raise AttributeError("Failed to determine video resolution, frame rate, or cache")
    writer = _VideoWriter(file, _VideoWriter_fourcc(*"mp4v"), fps, resolution)
    for row in dataset:
        try:
            writer.write(cache := _cvtColor(_array(_decode_frame(row, channel)), _COLOR_RGB2BGR))
        except (ValueError, _BinasciiError, _UnidentifiedImageError):
            writer.write(cache)
    writer.release()
