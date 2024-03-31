from tkinter import Misc as _Misc, Event as _Event
from typing import Callable as _Callable, override as _override

from customtkinter import StringVar as _StringVar

from leads_gui.prototype import CanvasBased, TextBased
from leads_gui.types import Font as _Font, Color as _Color


class Typography(TextBased):
    def __init__(self,
                 master: _Misc,
                 theme_key: str = "CTkLabel",
                 width: float = 0,
                 height: float = 0,
                 variable: _StringVar | None = None,
                 font: _Font | None = None,
                 text_color: _Color | None = None,
                 fg_color: _Color | None = None,
                 hover_color: _Color | None = None,
                 bg_color: _Color | None = None,
                 corner_radius: int | None = None,
                 clickable: bool = False,
                 command: _Callable[[_Event], None] = lambda _: None) -> None:
        super().__init__(master, theme_key, width, height, font, text_color, fg_color, hover_color, bg_color,
                         corner_radius, clickable, command)
        self._variable: _StringVar = variable if variable else _StringVar(master)
        self._variable.trace_add("write", lambda _, __, ___: self.render())

    @_override
    def raw_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear()
        v = self._variable.get()
        w, h = canvas.winfo_width(), canvas.winfo_height()
        font = self._font
        if (target_font_size := h - 28) < font[1]:
            font = (font[0], target_font_size)
        canvas.draw_fg(canvas)
        canvas._ids.append(canvas.create_text(w * .5, h * .5, text=v, justify="center", fill=self._text_color,
                                              font=font))
