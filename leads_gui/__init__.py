from importlib.util import find_spec as _find_spec

if not _find_spec("PIL"):
    raise ImportError("Please install `Pillow` to run this module\n>>>pip install Pillow")
if not _find_spec("customtkinter"):
    raise ImportError("Please install `customtkinter` to run this module\n>>>pip install customtkinter")

from os.path import abspath as _abspath
from typing import Callable as _Callable, Any as _Any
from customtkinter import set_default_color_theme as _set_default_color_theme

from leads import LEADS as _LEADS, Controller as _Controller
from leads_gui.prototype import *
from leads_gui.config import *
from leads_gui.icons import *
from leads_gui.accelerometer import *
from leads_gui.speedometer import *
from leads_gui.typography import *
from leads_gui.proxy import *
from leads_gui.performance_checker import *

_set_default_color_theme(f"{_abspath(__file__)[:-11]}assets/leads-theme.json")


def initialize(window: Window,
               render: _Callable[[ContextManager], None],
               leads: _LEADS[_Any],
               main_controller: _Controller) -> ContextManager:
    ctx = ContextManager(window)
    render(ctx)

    def on_refresh(_) -> None:
        leads.push(main_controller.read())
        leads.update()

    window.set_on_refresh(on_refresh)
    return ctx
