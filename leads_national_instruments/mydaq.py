from typing import override as _override

from nidaqmx import Task as _Task

from leads import Device as _Device


class MyDAQ(_Device):
    def __init__(self) -> None:
        super().__init__()
        self._task: _Task = _Task()

    @_override
    def close(self) -> None:
        self._task.close()
