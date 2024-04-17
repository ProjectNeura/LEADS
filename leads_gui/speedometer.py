from tkinter import Misc as _Misc, ARC as _ARC
from typing import override as _override, Literal as _Literal

from customtkinter import DoubleVar as _DoubleVar
from numpy import pi as _pi, sin as _sin, cos as _cos

from leads import require_config as _require_config
from leads_gui.prototype import parse_color, CanvasBased, TextBased, VariableControlled, autoscale_font
from leads_gui.types import Font as _Font, Color as _Color


class Speedometer(TextBased, VariableControlled):
    def __init__(self,
                 master: _Misc,
                 theme_key: str = "CTkButton",
                 width: float = 0,
                 height: float = 0,
                 variable: _DoubleVar | None = None,
                 style: _Literal[0, 1, 2] = 0,
                 next_style_on_click: bool = True,
                 maximum: float = 200,
                 font: tuple[_Font, _Font, _Font] | None = None,
                 text_color: _Color | None = None,
                 fg_color: _Color | None = None,
                 hover_color: _Color | None = None,
                 bg_color: _Color | None = None,
                 corner_radius: float | None = None) -> None:
        TextBased.__init__(self, master, theme_key, width, height, None, text_color, fg_color, hover_color, bg_color,
                           corner_radius, next_style_on_click,
                           lambda _: self.next_style() if next_style_on_click else lambda _: None)
        VariableControlled.__init__(self, variable if variable else _DoubleVar(master))
        self.attach(self.partially_render)
        self._style: _Literal[0, 1, 2] = style
        self._maximum: float = maximum
        cfg = _require_config()
        self._font: tuple[_Font, _Font, _Font] = font if font else (("Arial", cfg.font_size_x_large),
                                                                    ("Arial", cfg.font_size_large),
                                                                    ("Arial", cfg.font_size_small))
        self._font: tuple[_Font, _Font, _Font] = (
            autoscale_font(master, font[0]), autoscale_font(master, font[1]), autoscale_font(master, font[2])
        ) if font else (autoscale_font(master, ("Arial", cfg.font_size_x_large)),
                        autoscale_font(master, ("Arial", cfg.font_size_large)),
                        autoscale_font(master, ("Arial", cfg.font_size_small)))

    def next_style(self) -> None:
        self._style = (self._style + 1) % 3
        self.render()

    def style(self, style: _Literal[0, 1, 2] | None) -> _Literal[0, 1, 2] | None:
        if style is None:
            return self._style
        self._style = style
        self.render()

    @_override
    def dynamic_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear("d")
        v = self._variable.get()
        w, h, hc, vc, limit = canvas.meta()
        font = self._font[self._style]
        if self._style > 0:
            r = min(hc, vc) * 1.2
            x, y = hc, vc + r * .25
            p = min(v / self._maximum, 1)
            rad = p * 4 * _pi / 3 - _pi / 6
            color = parse_color((f"#{f"{int(0xbf - p * 0xbf):02x}" * 3}",
                                 f"#{f"{int(0x4d + 0xb2 * p):02x}" * 3}"))
            canvas.collect("d0", canvas.create_arc(x - r, y - r, x + r, y + r, start=-30, extent=240, width=4,
                                                   style=_ARC, outline=color))
            canvas.collect("d1", canvas.create_line(*(x, y) if self._style == 2 else (x - _cos(rad) * (r - 8),
                                                                                      y - _sin(rad) * (r - 8)),
                                                    x - _cos(rad) * (r + 8), y - _sin(rad) * (r + 8), width=4,
                                                    fill=color))
            canvas.collect("d2", canvas.create_text(x, y * .95 if self._style == 1 else y + (r - font[1]) * .5,
                                                    text=str(int(v)), fill=self._text_color, font=font))
        else:
            canvas.collect("d2", canvas.create_text(hc, vc, text=str(int(v)), fill=self._text_color, font=font))

    @_override
    def raw_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear()
        w, h, hc, vc, limit = canvas.meta()
        font = self._font[self._style]
        if (target_font_size := h - 28 if self._style == 0 else h - 48) < font[1]:
            font = (font[0], target_font_size)
        canvas.draw_fg(self._fg_color, self._hover_color, self._corner_radius)
        if self._style > 0:
            r = min(hc, vc) * 1.2
            x, y = hc, vc + r * .25
            font_size_span = int(min(h * .06, self._font[2][1] * .8))
            canvas.collect("f1", canvas.create_text(x, y - r * .6, text="KM / H", fill="gray",
                                                    font=(font[0], font_size_span)))
            canvas.collect("f2", canvas.create_text(x - r * .7, y + r * .4, text="0", fill="gray",
                                                    font=(font[0], font_size_span)))
            canvas.collect("f3", canvas.create_text(x + r * .7, y + r * .4, text=str(self._maximum), fill="gray",
                                                    font=(font[0], font_size_span)))
        self.dynamic_renderer(canvas)
