from tkinter import Misc as _Misc
from typing import Self as _Self, override as _override

from leads_gui.prototype import CanvasBased
from leads_gui.types import Color as _Color


class ProxyCanvas(CanvasBased):
    def __init__(self,
                 master: _Misc,
                 theme_key: str,
                 *canvases: CanvasBased,
                 mode: int = 0,
                 width: float = 0,
                 height: float = 0,
                 fg_color: _Color | None = None,
                 hover_color: _Color | None = None,
                 bg_color: _Color | None = None,
                 corner_radius: int | None = None) -> None:
        super().__init__(master, theme_key, width, height, fg_color, hover_color, bg_color, corner_radius, True,
                         lambda _: self.next_mode())
        self._canvases: tuple[CanvasBased, ...] = canvases
        self._mode: int = mode

    def next_mode(self) -> None:
        self._mode = (self._mode + 1) % len(self._canvases)

    def mode(self, mode: int | None = None) -> int | None:
        if self._mode is None:
            return self._mode
        self._mode = mode

    @_override
    def raw_renderer(self, canvas: _Self) -> None:
        self._canvases[self._mode].concurrent_raw_renderer(canvas)
