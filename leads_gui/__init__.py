from importlib.util import find_spec as _find_spec

if not _find_spec("customtkinter"):
    raise ImportError("Please install `customtkinter` to run this module\n>>>pip install customtkinter")

from os.path import abspath as _abspath
from typing import Callable as _Callable, Any as _Any
from customtkinter import set_default_color_theme as _set_default_color_theme

from leads import LEADS as _LEADS, Controller as _Controller
from leads.comm import Server as _Server, create_server as _create_server
from leads_gui.prototype import *
from leads_gui.runtime import *
from leads_gui.config import *

_set_default_color_theme(_abspath(__file__)[:-11] + "leads-theme.json")


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


def initialize_comm_server(window: Window,
                           render: _Callable[[ContextManager], None],
                           server: _Server = _create_server()) -> None:
    ctx = ContextManager(window)
    render(ctx)
    server.start(True)

    def on_close(_):
        server.kill()

    window.set_on_close(on_close)
