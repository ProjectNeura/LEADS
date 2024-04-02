from time import time as _time

from leads import require_config as _require_config


class PerformanceChecker(object):
    def __init__(self) -> None:
        self._refresh_rate: int = _require_config().refresh_rate
        self._fps: float = 0
        self._delay_offset: float = 0
        self._last_frame: float = _time()

    def fps(self) -> float:
        return self._fps

    def record_frame(self) -> None:
        # add .001 to avoid zero division
        delay = .001 + (t := _time()) - self._last_frame
        self._fps = 1 / delay
        self._delay_offset = (self._delay_offset * (self._refresh_rate - 1) + delay) / self._refresh_rate
        self._last_frame = t

    def delay_offset(self) -> float:
        return self._delay_offset * 1000
