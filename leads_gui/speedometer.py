from tkinter import Misc as _Misc, Event as _Event, ARC as _ARC
from typing import Callable as _Callable, override as _override

from customtkinter import DoubleVar as _DoubleVar, ThemeManager as _Theme
from numpy import pi as _pi, sin as _sin, cos as _cos

from leads import require_config as _require_config
from leads_gui.prototype import parse_color, CanvasBased
from leads_gui.types import Font as _Font, Color as _Color


class Speedometer(CanvasBased):
    def __init__(self,
                 master: _Misc,
                 width: int = 0,
                 height: int = 0,
                 variable: _DoubleVar | None = None,
                 style: int = 0,
                 next_style_on_click: bool = True,
                 maximum: float = 200,
                 font: tuple[_Font, _Font, _Font] | None = None,
                 text_color: _Color | None = None,
                 fg_color: _Color | None = None,
                 bg_color: _Color | None = None,
                 corner_radius: int | None = None,
                 command: _Callable[[_Event], None] = lambda _: None) -> None:
        super().__init__(master, width, height, bg_color, command)
        self._variable: _DoubleVar = variable if variable else _DoubleVar(master)
        self._maximum: float = maximum
        cfg = _require_config()
        self._font: tuple[_Font, _Font, _Font] = font if font else (("Arial", cfg.font_size_x_large),
                                                                    ("Arial", cfg.font_size_large),
                                                                    ("Arial", cfg.font_size_small))
        self._text_color: str = parse_color(text_color if text_color else _Theme.theme["CTkButton"]["text_color"])
        self._fg_color: str = parse_color(fg_color if fg_color else _Theme.theme["CTkButton"]["fg_color"])
        self._corner_radius: int = _Theme.theme["CTkButton"][
            "corner_radius"] if corner_radius is None else corner_radius
        self._variable.trace_add("write", lambda _, __, ___: self.render())
        self._style: int = style
        if next_style_on_click:
            def on_click(_) -> None:
                self._style = (self._style + 1) % 3

            self.bind("<Button-1>", on_click)

    @_override
    def raw_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear()
        v = self._variable.get()
        w, h = canvas.winfo_width(), canvas.winfo_height()
        hc, vc = w / 2, h / 2
        font = self._font[self._style]
        target_font_size = h - 28 if self._style == 0 else h - 48
        if target_font_size < font[1]:
            font = (font[0], target_font_size)

        r = self._corner_radius
        canvas._ids.append(
            canvas.create_polygon((r, 0, r, 0, w - r, 0, w - r, 0, w, 0, w, r, w, r, w, h - r, w, h - r, w,
                                   h, w - r, h, w - r, h, r, h, r, h, 0, h, 0, h - r, 0, h - r, 0, r, 0, r,
                                   0, 0), smooth=True, fill=self._fg_color))
        if self._style > 0:
            x, y = hc, vc + 16
            r = min(hc, vc) + 10
            p = min(v / self._maximum, 1)
            color = parse_color(("#" + str(int(60 - p * 60)) * 3, "#" + str(int(40 + p * 60)) * 3))
            canvas._ids.append(canvas.create_arc(x - r, y - r, x + r, y + r, start=-30, extent=240, width=4,
                                                 style=_ARC, outline=color))
            canvas._ids.append(canvas.create_text(x - r + 22,
                                                  y + r / 2 - 10,
                                                  text="0",
                                                  fill="gray",
                                                  font=("Arial", 8)))
            canvas._ids.append(canvas.create_text(x + r - 22,
                                                  y + r / 2 - 10,
                                                  text=str(self._maximum),
                                                  fill="gray",
                                                  font=("Arial", 8)))
            rad = p * 4 * _pi / 3 - _pi / 6
            canvas._ids.append(canvas.create_line(*(x, y) if self._style == 2 else (x - _cos(rad) * (r - 8),
                                                                                    y - _sin(rad) * (r - 8)),
                                                  x - _cos(rad) * (r + 8), y - _sin(rad) * (r + 8), width=4,
                                                  fill=color))
        canvas._ids.append(canvas.create_text(hc,
                                              vc if self._style == 0 else vc + 8 if self._style == 1 else h - font[1],
                                              text=str(int(v)), fill=self._text_color, font=font))
