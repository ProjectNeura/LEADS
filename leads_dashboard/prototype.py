from tkinter import Tk as _Tk
from tkinter import Widget as _Widget
from typing import Any as _Any, Callable as _Callable, Self as _Self, TypeVar as _TypeVar, Generic as _Generic

from leads_dashboard.runtime import RuntimeData


def default_on_refresh() -> None:
    pass


def default_on_kill() -> None:
    pass


Widget = _Widget | _Any

T = _TypeVar("T", bound=RuntimeData)


class Window(_Generic[T]):
    def __init__(self,
                 width: int,
                 height: int,
                 refresh_rate: int,
                 runtime_data: T,
                 fullscreen: bool = False,
                 on_refresh: _Callable[[_Self], None] = default_on_refresh,
                 on_kill: _Callable[[_Self], None] = default_on_kill,
                 title: str = "LEADS") -> None:
        self._root: _Tk = _Tk()
        self._root.title(title)
        self._root.columnconfigure(20, weight=1)
        width = self._root.winfo_screenwidth() if width < 0 else width
        height = self._root.winfo_screenheight() if height < 0 else height
        self._root.geometry(f"{width}x{height}")
        self._width: int = width
        self._height: int = height
        if fullscreen:
            self._root.attributes("-fullscreen", True)
        self._refresh_rate: int = refresh_rate
        self._refresh_interval: int = int(1000 / refresh_rate)
        self._runtime_data: T = runtime_data
        self._on_refresh: _Callable[[_Self], None] = on_refresh
        self._on_kill: _Callable[[_Self], None] = on_kill

    def root(self) -> _Tk:
        return self._root

    def width(self) -> int:
        return self._width

    def height(self) -> int:
        return self._height

    def refresh_interval(self) -> int:
        return self._refresh_interval

    def refresh_rate(self) -> int:
        return self._refresh_rate

    def runtime_data(self) -> T:
        return self._runtime_data

    def set_on_refresh(self, on_refresh: _Callable[[_Self], None]) -> None:
        self._on_refresh = on_refresh

    def set_on_close(self, on_close: _Callable[[_Self], None]) -> None:
        self._on_kill = on_close

    def show(self) -> None:
        def refresh():
            self._on_refresh(self)
            self._runtime_data.frame_counter += 1
            self._root.after(self._refresh_interval, refresh)

        self._root.after(self._refresh_interval, refresh)
        self._root.mainloop()

    def kill(self) -> None:
        self._root.destroy()


class ContextManager(object):
    def __init__(self, window: Window) -> None:
        self._window: Window = window
        self._widgets: dict[str, Widget] = {}

    def __setitem__(self, key: str, widget: Widget) -> None:
        self.set(key, widget)

    def __getitem__(self, key: str) -> Widget:
        return self.get(key)

    def set(self, key: str, widget: Widget) -> None:
        self._widgets[key] = widget

    def get(self, key: str) -> Widget:
        return self._widgets[key]

    def window(self) -> Window:
        return self._window

    def rd(self) -> T:
        return self._window.runtime_data()

    def root(self) -> _Tk:
        return self._window.root()

    def show(self) -> None:
        self._window.show()
