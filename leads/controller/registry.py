from typing import Any as _Any, Callable as _Callable, Sequence as _Sequence

from leads.controller.controller import Controller
from leads.controller.device import Device

_controllers: dict[str, Controller] = {}


def controller(tag: str,
               parent: str | None = None,
               args: tuple[_Any] = (),
               kwargs: dict[str, _Any] | None = None) -> _Callable[[type], None]:
    if tag in _controllers:
        raise RuntimeError(f"Cannot register: tag \"{tag}\" is already used")
    if parent:
        p = _controllers[parent]
    if not kwargs:
        kwargs = {}

    def _(target: type) -> None:
        if not issubclass(target, Controller):
            raise TypeError("Controllers must inherit from `Controller`")
        instance = target(*args, **kwargs)
        instance.tag(tag)
        _controllers[tag] = instance
        if parent:
            p.device(tag, instance)

    return _


def _register_device(prototype: type,
                     tag: str,
                     parent: Controller,
                     args: tuple[_Any],
                     kwargs: dict[str, _Any]) -> None:
    instance = prototype(*args, **kwargs)
    instance.tag(tag)
    parent.device(tag, instance)


def device(tag: str | _Sequence[str],
           parent: str,
           args: tuple[_Any] | list[tuple[_Any]] = (),
           kwargs: dict[str, _Any] | list[dict[str, _Any]] | None = None) -> _Callable[[type], None]:
    if isinstance(tag, str):
        tag = [tag]
    p = _controllers[parent]
    if isinstance(args, tuple):
        args = [args]
    if not kwargs:
        kwargs = [{}]
    elif isinstance(kwargs, dict):
        kwargs = [kwargs]

    def _(target: type) -> None:
        if not issubclass(target, Device):
            raise TypeError("Devices must inherit from `Device`")
        for i in range(len(tag)):
            _register_device(target, tag[i], p, args[i], kwargs[i])

    return _


def get_controller(tag: str) -> Controller:
    return _controllers[tag]


@controller("main", args=(1,))
class A(Controller[str]):
    def read(self) -> str:
        return ""
