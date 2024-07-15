from tkinter import Misc as _Misc, Event as _Event
from typing import Callable as _Callable, override as _override

from PIL.Image import Image as _Image
from PIL.ImageTk import PhotoImage as _PhotoImage
from customtkinter import Variable as _Variable, StringVar as _StringVar

from leads_gui.prototype import CanvasBased, VariableControlled
from leads_gui.types import Color as _Color
from leads_video import base64_decode_image as _base64_decode_image


class ImageVariable(_Variable):
    def __init__(self, master: _Misc, image: _Image | None, name: str | None = None) -> None:
        super().__init__(master, False, name)
        self._image: _Image | None = image

    @_override
    def set(self, value: _Image | None) -> None:
        super().set(not super().get())
        self._image = value

    @_override
    def get(self) -> _Image | None:
        return self._image


class Photo(CanvasBased, VariableControlled):
    def __init__(self,
                 master: _Misc,
                 theme_key: str = "CTkLabel",
                 width: float = 0,
                 height: float = 0,
                 variable: _StringVar | ImageVariable | None = None,
                 fg_color: _Color | None = None,
                 hover_color: _Color | None = None,
                 bg_color: _Color | None = None,
                 corner_radius: float | None = None,
                 clickable: bool = False,
                 command: _Callable[[_Event], None] = lambda _: None) -> None:
        CanvasBased.__init__(self, master, theme_key, width, height, fg_color, hover_color, bg_color, corner_radius,
                             clickable, command)
        VariableControlled.__init__(self, variable if variable else _StringVar(master))
        self.attach(self.partially_render)
        self._image: _PhotoImage | None = None

    @_override
    def dynamic_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear("d")
        w, h, hc, vc, limit = canvas.meta()
        if image := self._variable.get():
            if isinstance(image, str):
                image = _base64_decode_image(image)
            self._image = _PhotoImage(image.resize((w, h)))
            canvas.collect("d0", canvas.create_image(hc, vc, image=self._image))

    @_override
    def raw_renderer(self, canvas: CanvasBased) -> None:
        canvas.clear()
        canvas.draw_fg(self._fg_color, self._hover_color, self._corner_radius)
        self.dynamic_renderer(canvas)
