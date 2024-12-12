from collections import deque as _deque
from time import time as _time

from numpy import average as _average, poly1d as _poly1d, polyfit as _polyfit

from leads import require_config as _require_config


class PerformanceChecker(object):
    def __init__(self) -> None:
        self._refresh_rate: int = _require_config().refresh_rate
        self._interval: float = 1 / self._refresh_rate
        self._time_seq: _deque[float] = _deque((_time(),), maxlen=self._refresh_rate * 10)
        self._delay_seq: _deque[float] = _deque((.001,), maxlen=self._refresh_rate * 10)
        self._net_delay_seq: _deque[float] = _deque((.001,), maxlen=self._refresh_rate * 10)
        self._model: _poly1d | None = None
        self._last_frame: float = _time()

    def frame_rate(self) -> float:
        return 1 / _average(self._delay_seq)

    def net_delay(self) -> float:
        return float(_average(self._net_delay_seq))

    def record_frame(self, last_interval: float) -> None:
        # add .0000000001 to avoid zero division
        self._time_seq.append(t := _time())
        self._delay_seq.append(delay := .0000000001 + t - self._last_frame)
        self._net_delay_seq.append(delay - last_interval)
        self._model = _poly1d(_polyfit(self._time_seq, self._net_delay_seq, 5))
        self._last_frame = t

    def next_interval(self) -> float:
        return self._interval - max(min(self._model(_time()) if len(self._net_delay_seq) > self._refresh_rate else 0,
                                        self._interval - .001), 0)
