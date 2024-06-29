from typing import override as _override

from cv2 import VideoCapture as _VideoCapture, cvtColor as _cvtColor, COLOR_BGR2RGB as _COLOR_BGR2RGB
from numpy import ndarray as _ndarray

from leads import Device as _Device


class Camera(_Device):
    def __init__(self, port: int) -> None:
        super().__init__(port)
        self._video_capture: _VideoCapture | None = None
        self._resolution: tuple[int, int] | None = None

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self._video_capture = _VideoCapture(self._pins[0])

    @_override
    def write(self, payload: tuple[int, int] | None) -> None:
        self._resolution = payload

    @_override
    def read(self) -> _ndarray:
        _, frame = self._video_capture.read()
        return _cvtColor(frame, _COLOR_BGR2RGB)

    @_override
    def close(self) -> None:
        self._video_capture.release()
