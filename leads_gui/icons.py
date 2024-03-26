from enum import StrEnum as _StrEnum
from typing import Callable as _Callable

from PIL import Image as _Image
from customtkinter import CTkImage as _CTkImage

from leads import set_on_register_config as _set_on_register_config, OnRegister as _OnRegister, \
    get_config as _get_config
from leads_gui.config import Config
from leads_gui.system import _ASSETS_PATH

_ICONS_PATH: str = _ASSETS_PATH + "/icons"

_config: Config = _get_config()
if _config is None:
    _config = Config({})


def _on_register_config(chain: _OnRegister[Config] | None) -> _OnRegister[Config]:
    def _(config: Config) -> None:
        global _config
        if chain:
            chain(config)
        _config = config

    return _


_set_on_register_config(_on_register_config)


class Color(_StrEnum):
    BLACK: str = "black"
    WHITE: str = "white"
    RED: str = "red"


class _Icon(_Callable[[int, Color | None], _CTkImage]):
    def __init__(self, name: str) -> None:
        self._name: str = name

    def load_source(self, color: Color) -> _Image:
        return _Image.open(f"{_ICONS_PATH}/{self._name}-{color}.png")

    def __call__(self, size: int | None = None, color: Color | None = None) -> _CTkImage:
        if size is None:
            size = _config.w_font_size_medium
        return _CTkImage(self.load_source(color if color else Color.BLACK),
                         None if color else self.load_source(Color.WHITE),
                         size=(size, size))


Battery: _Icon = _Icon("battery")
Brake: _Icon = _Icon("brake")
ECS: _Icon = _Icon("ecs")
Engine: _Icon = _Icon("engine")
Hazard: _Icon = _Icon("hazard")
HighBeam: _Icon = _Icon("high-beam")
Light: _Icon = _Icon("light")
Motor: _Icon = _Icon("motor")
Satellite: _Icon = _Icon("satellite")
Speed: _Icon = _Icon("speed")
