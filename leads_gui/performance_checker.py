from collections import deque as _deque
from time import time as _time

from numpy import average as _average, poly1d as _poly1d, polyfit as _polyfit

from leads import require_config as _require_config


class PerformanceChecker(object):
    def __init__(self) -> None:
        self._refresh_rate: int = _require_config().refresh_rate
        self._original_interval: float = 1 / self._refresh_rate
        self._fps: float = 0
        self._predicted_offset: float = 0
        self._interval_seq: _deque[float] = _deque(maxlen=self._refresh_rate * 10)
        self._delay_seq: _deque[float] = _deque(maxlen=self._refresh_rate * 10)
        self._last_frame: float = _time()

    def fps(self) -> float:
        return self._fps

    def record_frame(self) -> None:
        # add .0000000001 to avoid zero division
        self._interval_seq.append(interval := .0000000001 + (t := _time()) - self._last_frame)
        self._delay_seq.append(interval - self._predicted_offset)
        self._fps = 1 / _average(self._interval_seq)
        mark = len(self._delay_seq)
        self._predicted_offset = max(min(_poly1d(_polyfit(range(mark), self._delay_seq, 5))(mark + 1)
                                         if mark > self._refresh_rate else 0,
                                         self._original_interval), 0)
        self._last_frame = t

    def next_interval(self) -> int:
        return int(1000 * self._original_interval - 1000 * self._predicted_offset)
