from threading import Thread as _Thread
from time import time as _time
from typing import override as _override

from PIL.Image import fromarray as _fromarray, Image as _Image
from cv2 import VideoCapture as _VideoCapture, cvtColor as _cvtColor, COLOR_BGR2RGB as _COLOR_BGR2RGB
from numpy import ndarray as _ndarray, pad as _pad, array as _array

from leads import Device as _Device, ShadowDevice as _ShadowDevice
from leads_video.base64 import base64_encode


class Camera(_Device):
    def __init__(self, port: int, resolution: tuple[int, int] | None = None) -> None:
        super().__init__(port)
        self._resolution: tuple[int, int] | None = resolution
        self._video_capture: _VideoCapture | None = None
        self._birth: float = 0

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self._video_capture = _VideoCapture(self._pins[0])

    @_override
    def write(self, payload: tuple[int, int] | None) -> None:
        """
        :param payload: [width, height]
        """
        self._resolution = payload

    def transform(self, x: _ndarray) -> _ndarray:
        height, width = x.shape[:-1]
        resolution_width, resolution_height = self._resolution
        target_ratio = resolution_height / resolution_width
        target_height = int(target_ratio * width)
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        if height > target_height:
            target_width = int(height / target_ratio)
            pad_left = (target_width - width) // 2
            pad_right = target_width - width - pad_left
        else:
            pad_top = (target_height - height) // 2
            pad_bottom = target_height - height - pad_top
        return _array(_fromarray(_pad(x, ((pad_left, pad_right), (pad_top, pad_bottom), (0, 0)))).resize(
            self._resolution))

    @_override
    def read(self) -> _ndarray | None:
        ret, frame = self._video_capture.read()
        self._birth = _time()
        return _cvtColor(self.transform(frame) if self._resolution else frame, _COLOR_BGR2RGB).transpose(
            2, 0, 1) if ret else None

    def read_numpy(self) -> _ndarray | None:
        return self.read()

    def read_pil(self) -> _Image | None:
        return None if (frame := self.read_numpy()) is None else _fromarray(frame.transpose(1, 2, 0))

    def latency(self) -> float:
        return _time() - self._birth

    @_override
    def close(self) -> None:
        self._video_capture.release()


class LowLatencyCamera(Camera, _ShadowDevice):
    def __init__(self, port: int, resolution: tuple[int, int] | None = None) -> None:
        Camera.__init__(self, port, resolution)
        _ShadowDevice.__init__(self, port)
        self._frame: _ndarray | None = None

    @_override
    def loop(self) -> None:
        if self._video_capture:
            self._frame = super().read()

    @_override
    def read(self) -> _ndarray | None:
        return self._frame


class Base64Camera(LowLatencyCamera):
    def __init__(self, port: int, resolution: tuple[int, int] | None = None) -> None:
        super().__init__(port, resolution)
        self._base64: str = ""

    @_override
    def loop(self) -> None:
        super().loop()
        if self._frame is not None:
            self._base64 = base64_encode(self._frame)

    @_override
    def read(self) -> str:
        return self._base64

    @_override
    def read_numpy(self) -> _ndarray | None:
        return self._frame


class LowLatencyBase64Camera(Base64Camera):
    def __init__(self, port: int, resolution: tuple[int, int] | None = None) -> None:
        super().__init__(port, resolution)
        self._shadow_thread2: _Thread | None = None

    @_override
    def loop(self) -> None:
        LowLatencyCamera.loop(self)

    def loop2(self) -> None:
        if (local_frame := self._frame) is not None:
            self._base64 = base64_encode(local_frame)

    def run2(self) -> None:
        while True:
            self.loop2()

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self._shadow_thread2 = _Thread(name=f"{id(self)} shadow2", target=self.run2, daemon=True)
        self._shadow_thread2.start()
