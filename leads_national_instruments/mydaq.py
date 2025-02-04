from typing import override as _override

try:
    from nidaqmx import Task as _Task
except ImportError as _e:
    raise ImportError(
        "If `nidaqmx` is installed, check if either NI-DAQmx or NI-DAQmx Runtime is not installed") from _e

from leads import Controller as _Controller, Device as _Device, get_controller as _get_controller


class AnalogInput(_Device):
    def __init__(self, channel: str) -> None:
        super().__init__(channel)

    @_override
    def initialize(self, *parent_tags: str) -> None:
        controller = _get_controller(parent_tags[-1])
        if isinstance(controller, MyDAQ):
            controller.task().ai_channels.add_ai_voltage_chan(self._pins[0])


class MyDAQ(_Controller):
    def __init__(self) -> None:
        super().__init__()
        self._task: _Task = _Task()

    def task(self) -> _Task:
        return self._task

    @_override
    def close(self) -> None:
        self._task.close()
