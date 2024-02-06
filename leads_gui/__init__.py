from importlib.util import find_spec as _find_spec

if not _find_spec("PySimpleGUI"):
    raise ImportError("Please install `pysimplegui` to run this module\n>>>pip install pysimplegui")

from typing import Callable as _Callable, Any as _Any

from leads import Leads as _Leads, Controller as _Controller
from leads.comm import Server as _Server, create_server as _create_server
from leads_gui.prototype import *
from leads_gui.runtime import *
from leads_gui.config import *


def initialize(window: Window,
               render: _Callable[[ContextManager], None],
               leads: _Leads[_Any],
               main_controller: _Controller) -> ContextManager:
    ctx = ContextManager(window)
    render(ctx)
    window.runtime_data().frame_counter = 0

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
