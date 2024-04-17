from enum import StrEnum as _StrEnum
from typing import Callable as _Callable, override as _override

from PIL import Image as _Image
from customtkinter import CTkImage as _CTkImage

from leads import require_config as _require_config
from leads_gui.system import _ASSETS_PATH

_ICONS_PATH: str = f"{_ASSETS_PATH}/icons"


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
            size = _require_config().font_size_medium
        return _CTkImage(self.load_source(color if color else Color.BLACK),
                         None if color else self.load_source(Color.WHITE),
                         size=(size, size))


class _Logo(_Icon):
    def __init__(self) -> None:
        super().__init__("logo")

    @_override
    def load_source(self, color: Color) -> _Image:
        return _Image.open(f"{_ASSETS_PATH}/logo.png")

    @_override
    def __call__(self, size: int | None = None, color: Color | None = None) -> _CTkImage:
        if size is None:
            size = _require_config().font_size_medium
        return _CTkImage(self.load_source(Color.BLACK), size=(size, size))


Logo: _Logo = _Logo()

Battery: _Icon = _Icon("battery")
Brake: _Icon = _Icon("brake")
Car: _Icon = _Icon("car")
ESC: _Icon = _Icon("esc")
Engine: _Icon = _Icon("engine")
Hazard: _Icon = _Icon("hazard")
HighBeam: _Icon = _Icon("high-beam")
Left: _Icon = _Icon("left")
Light: _Icon = _Icon("light")
Motor: _Icon = _Icon("motor")
Right: _Icon = _Icon("right")
Satellite: _Icon = _Icon("satellite")
Speed: _Icon = _Icon("speed")
Stopwatch: _Icon = _Icon("stopwatch")
