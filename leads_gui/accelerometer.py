from tkinter import Misc as _Misc
from typing import override as _override

from customtkinter import DoubleVar as _DoubleVar

from leads_gui.prototype import CanvasBased, TextBased
from leads_gui.types import Font as _Font, Color as _Color


class GForceMeter(TextBased):
    def __init__(self,
                 master: _Misc,
                 theme_key: str = "CTkButton",
                 width: float = 0,
                 height: float = 0,
                 variable: _DoubleVar | None = None,
                 font: _Font | None = None,
                 text_color: _Color | None = None,
                 fg_color: _Color | None = None,
                 hover_color: _Color | None = None,
                 bg_color: _Color | None = None,
                 corner_radius: int | None = None) -> None:
        super().__init__(master, theme_key, width, height, font, text_color, fg_color, hover_color, bg_color,
                         corner_radius)
        self._variable: _DoubleVar = variable if variable else _DoubleVar(master)

    @_override
    def raw_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear()
