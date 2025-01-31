from typing import override as _override

try:
    from nidaqmx import Task as _Task
except ImportError as _e:
    raise ImportError(
        "If `nidaqmx` is installed, check if either NI-DAQmx or NI-DAQmx Runtime is not installed") from _e

from leads import Device as _Device


class MyDAQ(_Device):
    def __init__(self) -> None:
        super().__init__()
        self._task: _Task = _Task()

    @_override
    def close(self) -> None:
        self._task.close()
