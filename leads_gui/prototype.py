from threading import Thread as _Thread
from time import sleep as _sleep
from typing import Callable as _Callable, Self as _Self, TypeVar as _TypeVar, Generic as _Generic

from PySimpleGUI import Window as _Window, Element as _Element, WINDOW_CLOSED as _WINDOW_CLOSED, theme as _theme

from leads_gui.runtime import RuntimeData
from leads_gui.system import get_system_platform


def default_on_refresh() -> None:
    pass


def default_on_kill() -> None:
    pass


Widget: type = _Element

T = _TypeVar("T", bound=RuntimeData)


class Window(_Generic[T]):
    def __init__(self,
                 width: int,
                 height: int,
                 refresh_rate: int,
                 runtime_data: T,
                 on_refresh: _Callable[[_Self], None] = default_on_refresh,
                 on_kill: _Callable[[_Self], None] = default_on_kill,
                 title: str = "LEADS",
                 fullscreen: bool = True,
                 no_title_bar: bool = True) -> None:
        _theme("Default1")
        self._root: _Window = _Window(title,
                                      size=(None if width < 0 else width, None if height < 0 else height),
                                      text_justification="center",
                                      no_titlebar=no_title_bar)
        self._width: int = _Window.get_screen_size()[0] if fullscreen else width
        self._height: int = _Window.get_screen_size()[1] if fullscreen else height
        self._fullscreen: bool = fullscreen
        self._refresh_rate: int = refresh_rate
        self._refresh_interval: float = float(1 / refresh_rate)
        self._runtime_data: T = runtime_data
        self._on_refresh: _Callable[[_Self], None] = on_refresh
        self._on_kill: _Callable[[_Self], None] = on_kill

        self._active: bool = False
        self._refresher_thread: _Thread | None = None

    def root(self) -> _Window:
        return self._root

    def width(self) -> int:
        return self._width

    def height(self) -> int:
        return self._height

    def refresh_interval(self) -> float:
        return self._refresh_interval

    def refresh_rate(self) -> int:
        return self._refresh_rate

    def runtime_data(self) -> T:
        return self._runtime_data

    def set_on_refresh(self, on_refresh: _Callable[[_Self], None]) -> None:
        self._on_refresh = on_refresh

    def set_on_close(self, on_close: _Callable[[_Self], None]) -> None:
        self._on_kill = on_close

    def active(self) -> bool:
        return self._active

    def refresher(self) -> None:
        while self._active:
            self._root.write_event_value("refresher", None)
            self._runtime_data.frame_counter += 1
            _sleep(self._refresh_interval)

    def show(self) -> None:
        self._root.finalize()
        if self._fullscreen:
            self._root.maximize()
        self._active = True
        self._refresher_thread = _Thread(name="refresher", target=self.refresher)
        self._refresher_thread.start()
        while self._active:
            event, values = self._root.read()
            if event == _WINDOW_CLOSED:
                self._active = False
                break
            elif event == "refresher":
                self._on_refresh(self)
            elif callable(event):
                event()

    def kill(self) -> None:
        self._active = False
        self._root.close()


class ContextManager(object):
    def __init__(self, window: Window) -> None:
        self._window: Window = window
        self._widgets: dict[str, Widget] = {}
        self._system_platform: str = get_system_platform()

    def __setitem__(self, key: str, widget: Widget) -> None:
        self._widgets[key] = widget

    def __getitem__(self, key: str) -> Widget:
        return self._widgets[key]

    def system_platform(self) -> str:
        return self._system_platform

    def set(self, key: str, widget: Widget) -> None:
        self[key] = widget

    def get(self, key: str) -> Widget:
        return self[key]

    def parse_layout(self, layout: list[list[str | Widget]]) -> list[list[Widget]]:
        for i in range(len(layout)):
            for j in range(len(layout[i])):
                e = layout[i][j]
                if isinstance(e, str):
                    layout[i][j] = self[e]
        return layout

    def layout(self, layout: list[list[str | Widget]]) -> None:
        self._window.root().layout(self.parse_layout(layout))

    def window(self) -> Window:
        return self._window

    def rd(self) -> T:
        return self._window.runtime_data()

    def active(self) -> bool:
        return self._window.active()

    def root(self) -> _Window:
        return self._window.root()

    def show(self) -> None:
        self._window.show()

    def kill(self) -> None:
        self._window.kill()
