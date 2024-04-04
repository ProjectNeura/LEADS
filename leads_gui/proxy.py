from tkinter import Misc as _Misc
from typing import override as _override

from leads_gui.prototype import CanvasBased, VariableControlled
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
                 corner_radius: float | None = None) -> None:
        super().__init__(master, theme_key, width, height, fg_color, hover_color, bg_color, corner_radius, True,
                         lambda _: self.next_mode())
        for canvas in canvases:
            if isinstance(canvas, VariableControlled):
                canvas.detach()
        self._canvases: tuple[CanvasBased, ...] = canvases
        self._mode: int = mode
        self._attach()

    def _attach(self) -> None:
        if isinstance(canvas := self._canvases[self._mode], VariableControlled):
            canvas.attach(self.partially_render)

    def next_mode(self) -> None:
        self.mode((self._mode + 1) % len(self._canvases))

    def mode(self, mode: int | None = None) -> int | None:
        if self._mode is None:
            return self._mode
        if isinstance(canvas := self._canvases[self._mode], VariableControlled):
            canvas.detach()
        self._mode = mode
        self.render()
        self._attach()

    @_override
    def dynamic_renderer(self, canvas: CanvasBased) -> None:
        self._canvases[self._mode].dynamic_renderer(canvas)

    @_override
    def raw_renderer(self, canvas: CanvasBased) -> None:
        self._canvases[self._mode].raw_renderer(canvas)
