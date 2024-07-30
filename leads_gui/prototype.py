from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from io import BytesIO as _BytesIO
from json import dumps as _dumps
from time import time as _time
from tkinter import Misc as _Misc, Event as _Event, PhotoImage as _PhotoImage
from typing import Callable as _Callable, Self as _Self, TypeVar as _TypeVar, Generic as _Generic, Any as _Any, \
    Literal as _Literal, override as _override

from PIL.Image import Image as _Image
from customtkinter import CTk as _CTk, CTkCanvas as _CTkCanvas, get_appearance_mode as _get_appearance_mode, \
    ThemeManager as _ThemeManager, Variable as _Variable, ScalingTracker as _ScalingTracker, \
    set_appearance_mode as _set_appearance_mode, CTkToplevel as _CTkToplevel
from numpy import lcm as _lcm
from screeninfo import get_monitors as _get_monitors

from leads import require_config as _require_config, DataContainer as _DataContainer
from leads.comm import Server as _Server
from leads_gui.performance_checker import PerformanceChecker
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
        self._last_width: float = self.meta()[0]
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

    def meta(self) -> tuple[float, float, float, float, float]:
        """
        :return: (w, h, hc, vc, limit)
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
        if self._ratio and (w := self.meta()[0]) != self._last_width:
            self.configure(height=w * self._ratio)
            self._last_width = w
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
        self._last_value: _Any = variable.get()
        self._trace_cb_name: str | None = None

    def attach(self, callback: _Callable[[], None]) -> None:
        if self._trace_cb_name:
            raise RuntimeError("Duplicated attachment")

        def unique(_, __, ___) -> None:
            if (v := self._variable.get()) != self._last_value:
                callback()
                self._last_value = v

        self._trace_cb_name = self._variable.trace_add("write", unique)

    def detach(self) -> None:
        if self._trace_cb_name:
            self._variable.trace_remove("write", self._trace_cb_name)
            self._trace_cb_name = None


class FrequencyGenerator(object, metaclass=_ABCMeta):
    def __init__(self, period: int, loops: int = -1) -> None:
        """
        :param period: the period in milliseconds
        :param loops: the number of loops or -1 to indicate infinite loops
        """
        self._period: int = period
        self._loops: int = loops
        self._last_run: float = 0

    @_abstractmethod
    def do(self) -> None:
        raise NotImplementedError

    def attempt(self) -> bool:
        """
        Attempt to run.
        :return: `True`: active; `False`: deprecated
        """
        if not self._loops:
            return False
        if (t := _time()) - self._last_run >= self._period * .001:
            self.do()
            self._loops -= 1
            self._last_run = t
        return True


class _RuntimeData(object):
    def __init__(self) -> None:
        self.root_window: Window | None = None
        self.start_time: int = int(_time())
        self.comm: _Server | None = None
        self.comm_stream: _Server | None = None

    def comm_notify(self, d: _DataContainer | dict[str, _Any]) -> None:
        if self.comm:
            self.comm.broadcast(d.encode() if isinstance(d, _DataContainer) else _dumps(d).encode())

    def comm_stream_notify(self, tag: _Literal["frvc", "lfvc", "rtvc", "revc"], frame: _Image,
                           quality: int = 90) -> None:
        if self.comm_stream:
            frame.save(buffer := _BytesIO(), "JPEG", quality=quality)
            self.comm_stream.broadcast(tag.encode() + b":" + buffer.getvalue())


_runtime_data_singleton_flag: bool = False


class RuntimeData(_RuntimeData):
    @_override
    def __new__(cls, *args, **kwargs) -> _RuntimeData:
        global _runtime_data_singleton_flag
        if _runtime_data_singleton_flag:
            raise ReferenceError("Multiple runtime data instances are not allowed")
        _runtime_data_singleton_flag = True
        return super().__new__(cls, *args, **kwargs)


T = _TypeVar("T", bound=RuntimeData)


class Window(_Generic[T]):
    def __init__(self,
                 width: int,
                 height: int,
                 refresh_rate: int,
                 runtime_data: T,
                 on_refresh: _Callable[[_Self], None] = lambda _: None,
                 title: str = "LEADS",
                 fullscreen: bool = False,
                 no_title_bar: bool = True,
                 theme_mode: _Literal["system", "light", "dark"] = "system",
                 display: int = 0,
                 yield_focus: bool = False) -> None:
        self._refresh_rate: int = refresh_rate
        self._runtime_data: T = runtime_data
        self._on_refresh: _Callable[[Window], None] = on_refresh
        self._frequency_generators: dict[str, FrequencyGenerator] = {}
        self._display: int = display
        self._yield_focus: bool = yield_focus

        if runtime_data.root_window:
            self._master: _CTkToplevel = _CTkToplevel(runtime_data.root_window.root())
            if yield_focus:
                self._master.bind("<Leave>", lambda _: runtime_data.root_window.root().focus_force())
            self.show()
        else:
            self._master: _CTk = _CTk()
            runtime_data.root_window = self
        screen = _get_monitors()[display]
        self._master.title(title)
        self._master.wm_iconbitmap()
        self._master.iconphoto(True, _PhotoImage(master=self._master, file=f"{_ASSETS_PATH}/logo.png"))
        self._master.overrideredirect(no_title_bar)
        _set_appearance_mode(theme_mode)
        self._screen_width: int = screen.width
        self._screen_height: int = screen.height
        self._width: int = self._screen_width if fullscreen else width
        self._height: int = self._screen_height if fullscreen else height

        x_offset = int((self._screen_width - self._width) * .5) + screen.x
        y_offset = int((self._screen_height - self._height) * .5)
        self._master.geometry(f"{self._width}x{self._height}+{x_offset}+{y_offset}")

        self._active: bool = isinstance(self._master, _CTkToplevel)
        self._performance_checker: PerformanceChecker = PerformanceChecker()
        self._last_interval: float = 0

    def root(self) -> _CTk:
        return self._master

    def is_true_root(self) -> bool:
        return isinstance(self._master, _CTk)

    def screen_index(self) -> int:
        return self._display

    def screen_width(self) -> int:
        return self._screen_width

    def screen_height(self) -> int:
        return self._screen_height

    def width(self) -> int:
        return self._width

    def height(self) -> int:
        return self._height

    def fps(self) -> float:
        return self._performance_checker.fps()

    def net_delay(self) -> float:
        return self._performance_checker.net_delay()

    def refresh_rate(self) -> int:
        return self._refresh_rate if isinstance(self._master, _CTk) else self._runtime_data.root_window.refresh_rate()

    def runtime_data(self) -> T:
        return self._runtime_data

    def set_on_refresh(self, on_refresh: _Callable[[_Self], None]) -> None:
        if isinstance(self._master, _CTkToplevel):
            raise NotImplementedError
        self._on_refresh = on_refresh

    def add_frequency_generator(self, tag: str, frequency_generator: FrequencyGenerator) -> None:
        if isinstance(self._master, _CTkToplevel):
            return self._runtime_data.root_window.add_frequency_generator(tag, frequency_generator)
        self._frequency_generators[tag] = frequency_generator

    def remove_frequency_generator(self, tag: str) -> None:
        try:
            self._frequency_generators.pop(tag)
        except KeyError:
            pass

    def clear_frequency_generators(self) -> None:
        if isinstance(self._master, _CTkToplevel):
            return self._runtime_data.root_window.clear_frequency_generators()
        self._frequency_generators.clear()

    def active(self) -> bool:
        return self._active if isinstance(self._master, _CTk) else self._runtime_data.root_window.active()

    def show(self) -> None:
        try:
            if isinstance(self._master, _CTkToplevel):
                if not self._yield_focus:
                    self._master.transient(self._runtime_data.root_window.root())
                self._master.focus_force()
                return
        finally:
            self._active = True

        def wrapper() -> None:
            self._on_refresh(self)
            for tag, fg in self._frequency_generators.items():
                if not fg.attempt():
                    self.remove_frequency_generator(tag)
            self._performance_checker.record_frame(self._last_interval)
            if self._active:
                self._master.after(int((ni := self._performance_checker.next_interval()) * 1000), wrapper)
                self._last_interval = ni

        self._master.after(1, wrapper)
        self._master.mainloop()

    def kill(self) -> None:
        self._active = False
        self._master.destroy()


class ContextManager(object):
    def __init__(self, *windows: Window) -> None:
        root_window = None
        self._windows: dict[int, Window] = {}
        for window in windows:
            if window.is_true_root():
                root_window = window
            else:
                self.add_window(window)
        if not root_window:
            raise LookupError("No root window")
        self._root_window: Window = root_window
        self._widgets: dict[str, _Widget] = {}

    def num_windows(self) -> int:
        return len(self._windows) + 1

    def _allocate_window(self) -> int:
        allocated_slots = self._windows.keys()
        if len(allocated_slots) == 0:
            return 0
        max_allocated_slot = max(allocated_slots)
        sparse_slots = set(range(max_allocated_slot)) - allocated_slots
        return min(sparse_slots) if len(sparse_slots) > 0 else max_allocated_slot + 1

    def add_window(self, window: Window) -> int:
        self._windows[index := self._allocate_window()] = window
        return index

    def remove_window(self, index: int) -> None:
        self._windows.pop(index)

    def index_of_window(self, window: Window) -> int:
        for k, v in self._windows.items():
            if v == window:
                return k
        return -1

    def __setitem__(self, key: str, widget: _Widget) -> None:
        self.set(key, widget)

    def __getitem__(self, key: str) -> _Widget:
        return self.get(key)

    def set(self, key: str, widget: _Widget) -> None:
        self._widgets[key] = widget

    def get(self, key: str) -> _Widget:
        return self._widgets[key]

    def parse_layout(self, layout: list[list[str | _Widget | None]]) -> list[list[_Widget | None]]:
        for i in range(len(layout)):
            for j in range(len(layout[i])):
                e = layout[i][j]
                if isinstance(e, str):
                    layout[i][j] = self[e]
        return layout

    def layout(self, layout: list[list[str | _Widget | None]], padding: float = .005, window_index: int = -1) -> None:
        window = self.window(window_index)
        layout = self.parse_layout(layout)
        root = window.root()
        root.grid_columnconfigure(tuple(range(t := _lcm.reduce(tuple(map(len, layout))))), weight=1)
        screen_width = window.screen_width()
        p = int(window.width() * padding)
        for i in range(len(layout)):
            row = layout[i]
            length = len(row)
            for j in range(length):
                if (widget := row[j]) is None:
                    continue
                s = int(t / length)
                widget.configure(width=screen_width)
                widget.grid(row=i, column=j * s, sticky="NSEW", columnspan=s, ipadx=p, ipady=p, padx=p, pady=p)

    def window(self, index: int = -1) -> Window:
        return self._root_window if index < 0 else self._windows[index]

    def show(self) -> None:
        self._root_window.show()

    def kill(self) -> None:
        self._root_window.kill()
