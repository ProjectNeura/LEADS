from typing import Any as _Any, Callable as _Callable, Sequence as _Sequence

from leads.dt.controller import Controller
from leads.dt.device import Device
from leads.dt.predefined_tags import MAIN_CONTROLLER

_controllers: dict[str, Controller] = {}


def controller(tag: str,
               parent: str | None = None,
               args: tuple[_Any, ...] = (),
               kwargs: dict[str, _Any] | None = None) -> _Callable[[type], None]:
    if not kwargs:
        kwargs = {}

    def _(target: type) -> None:
        if not issubclass(target, Controller):
            raise TypeError("Controllers must inherit from `Controller`")
        register_controller(tag, target(*args, **kwargs), parent)

    return _


def _register_device(prototype: type,
                     tag: str,
                     parent: Controller,
                     args: tuple[_Any, ...],
                     kwargs: dict[str, _Any]) -> None:
    instance = prototype(*args, **kwargs)
    parent.parent_tags(parent.parent_tags())
    parent.device(tag, instance)


def device(tag: str | _Sequence[str],
           parent: str | _Sequence[str],
           args: tuple[_Any, ...] | list[tuple[_Any, ...]] = (),
           kwargs: dict[str, _Any] | list[dict[str, _Any]] | None = None) -> _Callable[[type], None]:
    if isinstance(tag, str):
        tag = [tag]
    p = _controllers[parent]
    n = len(tag)
    if isinstance(parent, str):
        p = [parent] * n
    if isinstance(args, tuple):
        args = [args] * n
    if not kwargs:
        kwargs = [{}] * n
    elif isinstance(kwargs, dict):
        kwargs = [kwargs] * n

    def _(target: type) -> None:
        if not issubclass(target, Device):
            raise TypeError("Devices must inherit from `Device`")
        for i in range(len(tag)):
            _register_device(target, tag[i], p, args[i], kwargs[i])

    return _


def register_controller(tag: str, c: Controller, parent: str | None = None) -> None:
    if tag in _controllers:
        raise RuntimeError(f"Cannot register: tag \"{tag}\" is already used")
    if parent:
        c.parent_tags((p := _controllers[parent]).parent_tags() + c.parent_tags())
        p.device(tag, c)

    _controllers[tag] = c


def get_controller(tag: str) -> Controller:
    return _controllers[tag]


def initialize_main() -> None:
    get_controller(MAIN_CONTROLLER).initialize()
