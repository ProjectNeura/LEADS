from os.path import abspath as _abspath
from dearpygui import dearpygui as _dpg


_default_font: str = _abspath(__file__)[:-8] + "/_font/OpenSans-Regular.ttf"


def load_font(file: str = _default_font, size: int = 10) -> int | str:
    with _dpg.font_registry():
        return _dpg.add_font(file, size)
