from tkinter import Misc as _Misc
from typing import Self as _Self, override as _override

from leads_gui.prototype import CanvasBased
from leads_gui.types import Color as _Color


class ProxyCanvas(CanvasBased):
    def __init__(self,
                 master: _Misc,
                 *canvases: CanvasBased,
                 mode: int = 0,
                 width: int = 0,
                 height: int = 0,
                 bg_color: _Color | None = None) -> None:
        super().__init__(master, width, height, bg_color, lambda _: self.next_mode())
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
        self._canvases[self._mode].raw_renderer(canvas)
