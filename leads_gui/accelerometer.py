from tkinter import Misc as _Misc
from typing import override as _override

from PIL import ImageTk as _ImageTk
from customtkinter import Variable as _Variable, DoubleVar as _DoubleVar
from numpy import sqrt as _sqrt

from leads_gui.icons import Color, Car
from leads_gui.prototype import CanvasBased, TextBased, VariableControlled, parse_color
from leads_gui.types import Font as _Font, Color as _Color


class GForceVar(_Variable):
    def __init__(self, master: _Misc, x: float = 0, y: float = 0, name: str | None = None) -> None:
        super().__init__(master, (x, y), name)

    @_override
    def set(self, value: tuple[float, float]) -> None:
        super().set(value)

    @_override
    def get(self) -> tuple[float, float]:
        return super().get()

    def magnitude(self) -> float:
        return _sqrt((v := self.get())[0] ** 2 + v[1] ** 2)


class GForceMeter(TextBased, VariableControlled):
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
                 corner_radius: float | None = None) -> None:
        TextBased.__init__(self, master, theme_key, width, height, font, text_color, fg_color, hover_color, bg_color,
                           corner_radius)
        VariableControlled.__init__(self, variable if variable else GForceVar(master))
        self.attach(self.partially_render)
        self._max_magnitude: float = variable.magnitude()

    @_override
    def dynamic_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear("d")
        assert isinstance(self._variable, GForceVar)
        x, y = self._variable.get()
        if (magnitude := self._variable.magnitude()) > self._max_magnitude:
            self._max_magnitude = magnitude
        w, h, hc, vc, limit = canvas.meta()
        limit *= .5
        x, y = hc + max(min(x / 29.4, .9), -.9) * limit, vc + max(min(y / 29.4, .9), -.9) * limit
        r = max(min(self._max_magnitude / 29.4, .9), -.9) * limit
        canvas.collect("d0", canvas.create_oval(hc - r, vc - r, hc + r, vc + r, outline="green", width=2))
        canvas.collect("d1", canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=self._text_color))

    @_override
    def raw_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear()
        w, h, hc, vc, limit = canvas.meta()
        canvas.draw_fg(self._fg_color, self._hover_color, self._corner_radius)
        color = parse_color(("gray74", "gray60"))
        canvas.collect("f0", canvas.create_text(hc, vc, text="G", fill=self._text_color,
                                                font=(self._font[0], int(h * .1))))
        for factor in .9, .6, .3:
            r = limit * .5 * factor
            canvas.collect(f"f1{factor}", canvas.create_oval(hc - r, vc - r, hc + r, vc + r, outline=color, width=2))
        self.dynamic_renderer(canvas)


class SpeedTrendMeter(TextBased, VariableControlled):
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
                 corner_radius: float | None = None) -> None:
        TextBased.__init__(self, master, theme_key, width, height, font, text_color, fg_color, hover_color, bg_color,
                           corner_radius)
        VariableControlled.__init__(self, variable if variable else _DoubleVar(master))
        self.attach(self.partially_render)
        self._image: _ImageTk.PhotoImage | None = None

    @_override
    def dynamic_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear("d")
        v = self._variable.get()
        w, h, hc, vc, limit = canvas.meta()
        canvas.collect("d0", canvas.create_line(hc, vc, hc + max(min(v, .9), -.9) * hc, vc, fill=self._text_color,
                                                arrow="last", width=4))

    @_override
    def raw_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear()
        w, h, hc, vc, limit = canvas.meta()
        canvas.draw_fg(self._fg_color, self._hover_color, self._corner_radius)
        if self._image is None:
            self._image = _ImageTk.PhotoImage(Car.load_source(Color[parse_color(("BLACK", "WHITE"))]).resize((limit,
                                                                                                              limit)))
        canvas.collect("f0", canvas.create_image(hc, vc, image=self._image))
        self.dynamic_renderer(canvas)
