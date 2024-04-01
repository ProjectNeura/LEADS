from tkinter import Misc as _Misc
from typing import override as _override

from PIL import ImageTk as _ImageTk
from customtkinter import Variable as _Variable, DoubleVar as _DoubleVar

from leads_gui.icons import Color, Car
from leads_gui.prototype import CanvasBased, TextBased, parse_color
from leads_gui.types import Font as _Font, Color as _Color


class GForceVar(_Variable):
    def __init__(self, master: _Misc, *forces: float, name: str | None = None) -> None:
        super().__init__(master, forces, name)

    @_override
    def set(self, *forces: float) -> None:
        super().set(forces)

    @_override
    def get(self) -> tuple[float, ...]:
        return super().get()


class GForceMeter(TextBased):
    def __init__(self,
                 master: _Misc,
                 theme_key: str = "CTkButton",
                 width: float = 0,
                 height: float = 0,
                 variable: GForceVar | None = None,
                 font: _Font | None = None,
                 text_color: _Color | None = None,
                 fg_color: _Color | None = None,
                 hover_color: _Color | None = None,
                 bg_color: _Color | None = None,
                 corner_radius: int | None = None) -> None:
        super().__init__(master, theme_key, width, height, font, text_color, fg_color, hover_color, bg_color,
                         corner_radius)
        self._variable: GForceVar = variable if variable else GForceVar(master)

    @_override
    def raw_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear()
        canvas.draw_fg(self._fg_color, self._hover_color, self._corner_radius)
        # todo


class SpeedTrendMeter(TextBased):
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
        self._image: _ImageTk.PhotoImage | None = None

    @_override
    def raw_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear()
        v = self._variable.get() * 5
        w, h = canvas.winfo_width(), canvas.winfo_height()
        hc, vc = w * .5, h * .5
        limit = min(w, h)
        canvas.draw_fg(self._fg_color, self._hover_color, self._corner_radius)
        if self._image is None:
            self._image = _ImageTk.PhotoImage(Car.load_source(Color[parse_color(("BLACK", "WHITE"))]).resize((limit,
                                                                                                              limit)))
        canvas._ids.append(canvas.create_image(hc, vc, image=self._image))
        canvas._ids.append(canvas.create_line(hc, vc, hc + max(min(v, .9), -.9) * hc, vc, fill=self._text_color,
                                              arrow="last", width=4))
