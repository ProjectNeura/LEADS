from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from typing import override as _override

try:
    from nidaqmx import Task as _Task
except ImportError as _e:
    raise ImportError(
        "If `nidaqmx` is installed, check if either NI-DAQmx or NI-DAQmx Runtime is not installed") from _e

from leads import Controller as _Controller, Device as _Device, get_controller as _get_controller


class MyDAQDevice(_Device, metaclass=_ABCMeta):
    def __init__(self, channel: str) -> None:
        super().__init__(channel)

    @_abstractmethod
    @_override
    def initialize(self, *parent_tags: str) -> None:
        raise NotImplementedError


class DigitalInput(MyDAQDevice):
    @_override
    def initialize(self, *parent_tags: str) -> None:
        controller = _get_controller(parent_tags[-1])
        if isinstance(controller, MyDAQ):
            controller.task().di_channels.add_di_chan(f"{controller.port()}/{self._pins[0]}")


class DigitalOutput(MyDAQDevice):
    @_override
    def initialize(self, *parent_tags: str) -> None:
        controller = _get_controller(parent_tags[-1])
        if isinstance(controller, MyDAQ):
            controller.task().do_channels.add_do_chan(f"{controller.port()}/{self._pins[0]}")


class AnalogInput(MyDAQDevice):
    @_override
    def initialize(self, *parent_tags: str) -> None:
        controller = _get_controller(parent_tags[-1])
        if isinstance(controller, MyDAQ):
            controller.task().ai_channels.add_ai_voltage_chan(f"{controller.port()}/{self._pins[0]}")


class AnalogOutput(MyDAQDevice):
    @_override
    def initialize(self, *parent_tags: str) -> None:
        controller = _get_controller(parent_tags[-1])
        if isinstance(controller, MyDAQ):
            controller.task().ao_channels.add_ao_voltage_chan(f"{controller.port()}/{self._pins[0]}")


class MyDAQ(_Controller):
    def __init__(self, port: str) -> None:
        super().__init__()
        self._port: str = port
        self._task: _Task = _Task()

    def port(self) -> str:
        return self._port

    def task(self) -> _Task:
        return self._task

    @_override
    def close(self) -> None:
        self._task.close()
