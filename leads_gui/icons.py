from enum import StrEnum as _StrEnum
from os.path import abspath as _abspath

from PIL import Image as _Image
from customtkinter import CTkImage as _CTkImage

from leads import set_on_register_config as _set_on_register_config, OnRegisterConfig as _OnRegisterConfig, \
    get_config as _get_config
from leads_gui.config import Config

_ASSETS_PATH = _abspath(__file__)[:-8] + "assets"
_ICONS_PATH = _ASSETS_PATH + "/icons"

_config: Config = _get_config(Config)


class Color(_StrEnum):
    BLACK: str = "black"
    WHITE: str = "white"
    RED: str = "red"


class _Icon(object):
    def __init__(self, name: str) -> None:
        self._name: str = name

    def load_source(self, color: Color) -> _Image:
        return _Image.open(f"{_ICONS_PATH}/{self._name}-{color}.png")

    def __call__(self, size: int = _config.font_size_medium, color: Color = Color.BLACK) -> _CTkImage:
        return _CTkImage(self.load_source(color), self.load_source(Color.WHITE) if color == Color.BLACK else None,
                         size=(size, size))


Battery = _Icon("battery")
Brake = _Icon("brake")
ECS = _Icon("ecs")
Engine = _Icon("engine")
HighBeam = _Icon("high-beam")
Light = _Icon("light")
Motor = _Icon("motor")
Speed = _Icon("speed")


def _on_register_config(chain: _OnRegisterConfig[Config] | None) -> _OnRegisterConfig[Config]:
    def _(config: Config) -> None:
        global _config
        if chain:
            chain(config)
        _config = config

    return _


_set_on_register_config(_on_register_config)
if _c := _get_config(Config):
    _on_register_config(None)(_c)
