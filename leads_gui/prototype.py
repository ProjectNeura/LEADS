from tkinter import Misc as _Misc, Event as _Event
from typing import Callable as _Callable, Self as _Self, TypeVar as _TypeVar, Generic as _Generic, Any as _Any

from PIL import ImageTk as _ImageTk
from customtkinter import CTk as _CTk, CTkCanvas as _CTkCanvas, get_appearance_mode as _get_appearance_mode, \
    ThemeManager as _ThemeManager, Variable as _Variable, ScalingTracker as _ScalingTracker
from numpy import lcm as _lcm

from leads import require_config as _require_config
from leads_gui.performance_checker import PerformanceChecker
from leads_gui.runtime import RuntimeData
from leads_gui.system import _ASSETS_PATH
from leads_gui.types import Widget as _Widget, Color as _Color, Font as _Font


def parse_color(color: _Color) -> str:
    c = color if isinstance(color, str) else color[0] if _get_appearance_mode() == "Light" else color[1]
    return parse_color(_ThemeManager.theme["CTk"]["fg_color"]) if c == "transparent" else c


def autoscale(master: _Misc, s: float) -> float:
    return s * _ScalingTracker.get_widget_scaling(master)


def autoscale_font(master: _Misc, font: _Font) -> _Font:
    return font[0], int(autoscale(master, font[1]))


class CanvasBased(_CTkCanvas):
    def __init__(self,
                 master: _Misc,
                 theme_key: str,
                 width: float = 0,
                 height: float = 0,
                 fg_color: _Color | None = None,
                 hover_color: _Color | None = None,
                 bg_color: _Color | None = None,
                 corner_radius: float | None = None,
                 clickable: bool = False,
                 command: _Callable[[_Event], None] = lambda _: None) -> None:
        super().__init__(master, width=autoscale(master, width * master.winfo_width() if 0 < width < 1 else width),
                         height=autoscale(master, height * master.winfo_height() if 0 < height < 1 else height),
                         highlightthickness=0, cursor="hand2" if clickable else None,
                         background=parse_color(bg_color if bg_color else "transparent"))
        self._fg_color: str = parse_color(fg_color if fg_color else _ThemeManager.theme[theme_key]["fg_color"])
        self._hovering: bool = False
        try:
            self._hover_color: str = parse_color(hover_color if hover_color else _ThemeManager.theme[theme_key][
                "hover_color"])
            if clickable:
                def hover(_) -> None:
                    self._hovering = not self._hovering
                    self.render()

                self.bind("<Enter>", hover)
                self.bind("<Leave>", hover)
        except KeyError:
            self._hover_color: str = self._fg_color
        self._corner_radius: float = autoscale(master, _ThemeManager.theme[theme_key][
            "corner_radius"] if corner_radius is None else corner_radius)
        if clickable:
            self.bind("<Button-1>", command)
        self._ratio: float | None = None
        self._history_width: float = self.meta()[0]
        self._ids: dict[str, int] = {}
        self.bind("<Configure>", lambda _: self.render())

    def lock_ratio(self, ratio: float) -> _Self:
        """
        Adjust the height according to the width to keep a constant ratio.
        :param ratio: height / width
        :return: self
        """
        self._ratio = ratio
        return self

    def meta(self) -> [float, float, float, float, float]:
        """
        :return: [w, h, hc, vc, limit]
        """
        return (w := self.winfo_width()), (h := self.winfo_height()), w * .5, h * .5, min(w, h)

    def collect(self, tag: str, object_id: int) -> None:
        """
        Collect a widget and link it to the tag for recycling.
        :param tag: the widget tag
        :param object_id: the widget id returned during creation
        """
        self._ids[tag] = object_id

    def clear(self, prefix: str = "") -> None:
        """
        Recycle the widgets linked to tags that start with the specified prefix.
        :param prefix: the tag prefix
        """
        if prefix:
            for tag, object_id in self._ids.copy().items():
                if tag.startswith(prefix):
                    self.delete(object_id)
                    self._ids.pop(tag)
        else:
            self.delete(*self._ids.values())
            self._ids.clear()

    def draw_fg(self, fg_color: _Color, hover_color: _Color, corner_radius: float) -> None:
        meta = self.meta()
        w, h, r = meta[0], meta[1], corner_radius * 2
        self.collect("_fg", self.create_polygon((r, 0, r, 0, w - r, 0, w - r, 0, w, 0, w, r, w, r, w, h - r, w, h - r,
                                                 w, h, w - r, h, w - r, h, r, h, r, h, 0, h, 0, h - r, 0, h - r, 0, r,
                                                 0, r, 0, 0), smooth=True,
                                                fill=hover_color if self._hovering else fg_color))

    def dynamic_renderer(self, canvas: _Self) -> None:
        """
        The dynamic renderer should only render the content-based components.
        The dynamic renderer should only access the parameters from self, and then render on the specified canvas.
        :param canvas: the canvas to render on
        """
        ...

    def partially_render(self) -> None:
        self.dynamic_renderer(self)

    def raw_renderer(self, canvas: _Self) -> None:
        """
        The raw renderer should only access the parameters from self, and then render on the specified canvas.
        :param canvas: the canvas to render on
        """
        ...

    def render(self) -> None:
        if self._ratio and (w := self.meta()[0]) != self._history_width:
            self.configure(height=w * self._ratio)
            self._history_width = w
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
                 corner_radius: float | None = None,
                 clickable: bool = False,
                 command: _Callable[[_Event], None] = lambda _: None) -> None:
        super().__init__(master, theme_key, width, height, fg_color, hover_color, bg_color, corner_radius, clickable,
                         command)
        self._font: _Font = autoscale_font(master, font if font else ("Arial", _require_config().font_size_small))
        self._text_color: str = parse_color(text_color if text_color else _ThemeManager.theme[theme_key]["text_color"])


class VariableControlled(object):
    def __init__(self, variable: _Variable) -> None:
        self._variable: _Variable = variable
        self._history_value: _Any = variable.get()
        self._trace_cb_name: str | None = None

    def attach(self, callback: _Callable[[], None]) -> None:
        if self._trace_cb_name:
            raise RuntimeError("Duplicated attachment")

        def unique(_, __, ___) -> None:
            if (v := self._variable.get()) != self._history_value:
                callback()
                self._history_value = v

        self._trace_cb_name = self._variable.trace_add("write", unique)

    def detach(self) -> None:
        if self._trace_cb_name:
            self._variable.trace_remove("write", self._trace_cb_name)
            self._trace_cb_name = None


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

    def __setitem__(self, key: str, widget: _Widget) -> None:
        self._widgets[key] = widget

    def __getitem__(self, key: str) -> _Widget:
        return self._widgets[key]

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
        root = self._window.root()
        root.grid_columnconfigure(tuple(range(t := _lcm.reduce(tuple(map(len, layout))))), weight=1)
        screen_width = root.winfo_screenwidth()
        for i in range(len(layout)):
            row = layout[i]
            length = len(row)
            for j in range(length):
                widget = row[j]
                s = int(t / length)
                widget.configure(width=screen_width)
                widget.grid(row=i, column=j * s, sticky="NSEW", columnspan=s, ipadx=4, ipady=4, padx=4, pady=4)

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
