from collections import deque as _deque
from time import time as _time

from numpy import average as _average, poly1d as _poly1d, polyfit as _polyfit

from leads import require_config as _require_config


class PerformanceChecker(object):
    def __init__(self) -> None:
        self._refresh_rate: int = _require_config().refresh_rate
        self._original_interval: float = 1 / self._refresh_rate
        self._double_original_interval: float = 2 * self._original_interval
        self._fps: float = 0
        self._offset: float = 0
        self._delay_seq: _deque[float] = _deque(maxlen=self._refresh_rate * 10)
        self._last_frame: float = _time()

    def fps(self) -> float:
        return self._fps

    def record_frame(self) -> None:
        # add .001 to avoid zero division
        delay = .001 + (t := _time()) - self._last_frame
        self._delay_seq.append(delay)
        self._fps = 1 / _average(self._delay_seq)
        mark = len(self._delay_seq)
        self._offset = max(min(_poly1d(_polyfit(range(mark), self._delay_seq, 5))(mark + 1)
                               if mark > self._refresh_rate else self._original_interval,
                               self._double_original_interval), self._original_interval)
        self._last_frame = t

    def next_interval(self) -> int:
        # 1200 is determined by experiences
        return int(3000 * self._original_interval - 1000 * self._offset - 1200 / self._fps)
