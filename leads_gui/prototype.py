from tkinter import Misc as _Misc, Event as _Event
from typing import Callable as _Callable, Self as _Self, TypeVar as _TypeVar, Generic as _Generic

from PIL import ImageTk as _ImageTk
from customtkinter import CTk as _CTk, CTkCanvas as _CTkCanvas, get_appearance_mode as _get_appearance_mode, \
    ThemeManager as _ThemeManager
from numpy import lcm as _lcm

from leads import require_config as _require_config
from leads_gui.performance_checker import PerformanceChecker
from leads_gui.runtime import RuntimeData
from leads_gui.system import _ASSETS_PATH, get_system_platform as _get_system_platform
from leads_gui.types import Widget as _Widget, Color as _Color, Font as _Font

T = _TypeVar("T", bound=RuntimeData)


class Window(_Generic[T]):
    def __init__(self,
                 width: int,
                 height: int,
                 refresh_rate: int,
                 runtime_data: T,
                 on_refresh: _Callable[[_Self], None] = lambda _: None,
                 title: str = "LEADS",
                 fullscreen: bool = True,
                 no_title_bar: bool = True) -> None:
        self._root: _CTk = _CTk()
        self._root.title(title)
        self._root.wm_iconbitmap()
        self._root.iconphoto(True, _ImageTk.PhotoImage(file=_ASSETS_PATH + "/logo.png"))
        self._root.overrideredirect(no_title_bar)
        self._width: int = self._root.winfo_screenwidth() if fullscreen else width
        self._height: int = self._root.winfo_screenheight() if fullscreen else height
        self._root.geometry(str(self._width) + "x" + str(self._height))
        self._refresh_rate: int = refresh_rate
        self._refresh_interval: int = int(1000 / refresh_rate)
        self._runtime_data: T = runtime_data
        self._on_refresh: _Callable[[Window], None] = on_refresh

        self._active: bool = False
        self._performance_checker: PerformanceChecker = PerformanceChecker()

    def root(self) -> _CTk:
        return self._root

    def width(self) -> int:
        return self._width

    def height(self) -> int:
        return self._height

    def fps(self) -> float:
        return self._performance_checker.fps()

    def refresh_rate(self) -> int:
        return self._refresh_rate

    def runtime_data(self) -> T:
        return self._runtime_data

    def set_on_refresh(self, on_refresh: _Callable[[_Self], None]) -> None:
        self._on_refresh = on_refresh

    def active(self) -> bool:
        return self._active

    def show(self) -> None:
        self._active = True

        def wrapper() -> None:
            self._on_refresh(self)
            self._performance_checker.record_frame()
            if self._active:
                self._root.after(max(0, int(2 * self._refresh_interval - self._performance_checker.delay_offset())),
                                 wrapper)

        self._root.after(0, wrapper)
        self._root.mainloop()

    def kill(self) -> None:
        self._active = False
        self._root.destroy()


class ContextManager(object):
    def __init__(self, window: Window) -> None:
        self._window: Window = window
        self._widgets: dict[str, _Widget] = {}
        self._system_platform: str = _get_system_platform()

    def __setitem__(self, key: str, widget: _Widget) -> None:
        self._widgets[key] = widget

    def __getitem__(self, key: str) -> _Widget:
        return self._widgets[key]

    def system_platform(self) -> str:
        return self._system_platform

    def set(self, key: str, widget: _Widget) -> None:
        self[key] = widget

    def get(self, key: str) -> _Widget:
        return self[key]

    def parse_layout(self, layout: list[list[str | _Widget]]) -> list[list[_Widget]]:
        for i in range(len(layout)):
            for j in range(len(layout[i])):
                e = layout[i][j]
                if isinstance(e, str):
                    layout[i][j] = self[e]
        return layout

    def layout(self, layout: list[list[str | _Widget]]) -> None:
        layout = self.parse_layout(layout)
        self.root().grid_columnconfigure(tuple(range(t := _lcm.reduce(tuple(map(len, layout))))), weight=1)
        for i in range(len(layout)):
            row = layout[i]
            length = len(row)
            for j in range(length):
                s = int(t / length)
                row[j].grid(row=i, column=j * s, sticky="NSEW", columnspan=s, ipadx=4, ipady=4, padx=4, pady=4)

    def window(self) -> Window:
        return self._window

    def rd(self) -> T:
        return self._window.runtime_data()

    def active(self) -> bool:
        return self._window.active()

    def fps(self) -> float:
        return self._window.fps()

    def root(self) -> _CTk:
        return self._window.root()

    def show(self) -> None:
        self._window.show()

    def kill(self) -> None:
        self._window.kill()


def parse_color(color: _Color) -> str:
    c = color if isinstance(color, str) else color[0] if _get_appearance_mode() == "Light" else color[1]
    return parse_color(_ThemeManager.theme["CTk"]["fg_color"]) if c == "transparent" else c


class CanvasBased(_CTkCanvas):
    def __init__(self,
                 master: _Misc,
                 theme_key: str,
                 width: float = 0,
                 height: float = 0,
                 fg_color: _Color | None = None,
                 hover_color: _Color | None = None,
                 bg_color: _Color | None = None,
                 corner_radius: int | None = None,
                 clickable: bool = False,
                 command: _Callable[[_Event], None] = lambda _: None) -> None:
        super().__init__(master, width=width * master.winfo_width() if 0 < width < 1 else width,
                         height=height * master.winfo_height() if 0 < height < 1 else height,
                         highlightthickness=0, cursor="hand2" if clickable else None,
                         background=parse_color(bg_color if bg_color else _ThemeManager.theme["CTk"]["fg_color"]))
        self._fg_color: str = parse_color(fg_color if fg_color else _ThemeManager.theme[theme_key]["fg_color"])
        self._hovering: bool = False
        try:
            self._hover_color: str = parse_color(hover_color if hover_color else
                                                 _ThemeManager.theme[theme_key]["hover_color"])
            if clickable:
                def hover(_) -> None:
                    self._hovering = not self._hovering
                    self.render()

                self.bind("<Enter>", hover)
                self.bind("<Leave>", hover)
        except KeyError:
            self._hover_color: str = self._fg_color
        self._corner_radius: int = _ThemeManager.theme[theme_key][
            "corner_radius"] if corner_radius is None else corner_radius
        if clickable:
            self.bind("<Button-1>", command)
        self._ids: list[int] = []

    def clear(self) -> None:
        self.delete(*self._ids)
        self._ids.clear()

    def draw_fg(self, fg_color: _Color, hover_color: _Color, corner_radius: int) -> None:
        w, h, r = self.winfo_width(), self.winfo_height(), corner_radius
        self._ids.append(self.create_polygon((r, 0, r, 0, w - r, 0, w - r, 0, w, 0, w, r, w, r, w, h - r, w, h - r, w,
                                              h, w - r, h, w - r, h, r, h, r, h, 0, h, 0, h - r, 0, h - r, 0, r, 0, r,
                                              0, 0), smooth=True, fill=hover_color if self._hovering else fg_color))

    def raw_renderer(self, canvas: _Self) -> None:
        """
        The raw renderer should only access the parameters from self, and then render on the specified canvas.
        :param canvas: the canvas to render on
        """
        ...

    def render(self) -> None:
        self.raw_renderer(self)


class TextBased(CanvasBased):
    def __init__(self,
                 master: _Misc,
                 theme_key: str,
                 width: float = 0,
                 height: float = 0,
                 font: _Font | None = None,
                 text_color: _Color | None = None,
                 fg_color: _Color | None = None,
                 hover_color: _Color | None = None,
                 bg_color: _Color | None = None,
                 corner_radius: int | None = None,
                 clickable: bool = False,
                 command: _Callable[[_Event], None] = lambda _: None) -> None:
        super().__init__(master, theme_key, width, height, fg_color, hover_color, bg_color, corner_radius, clickable,
                         command)
        self._font: _Font = font if font else ("Arial", _require_config().font_size_small)
        self._text_color: str = parse_color(text_color if text_color else _ThemeManager.theme[theme_key]["text_color"])
