from time import sleep as _sleep
from dearpygui import dearpygui as _dpg
from leads import Leads as _Leads, Controller as _Controller
from typing import Callable as _Callable, TypeVar as _TypeVar

from .fonts import load_font
from .runtime import RuntimeData


_dpg.create_context()

H1 = load_font(size=100)
H2 = load_font(size=40)
H3 = load_font(size=30)
H4 = load_font(size=20)
H5 = load_font(size=10)
BODY = load_font(size=10)
BODY2 = load_font(size=6)

_dpg.create_viewport(title="LEADS")
_dpg.setup_dearpygui()


T = _TypeVar("T")


def start(render: _Callable,
          context: _Leads[T],
          main_controller: _Controller[T],
          analysis_rate: float = .01,
          update_rate: float = .5,
          runtime_data: RuntimeData = RuntimeData()):
    with _dpg.window(tag="main",
                     label="LEADS",
                     no_title_bar=True,
                     no_scrollbar=True,
                     menubar=False,
                     no_close=True,
                     no_background=True, ):
        render()
    _dpg.show_viewport()
    _dpg.set_primary_window("main", True)
    runtime_data.frame_counter = 0
    while _dpg.is_dearpygui_running():
        _sleep(analysis_rate)
        context.push(main_controller.collect_all())
        if runtime_data.frame_counter % (update_rate / analysis_rate) == 0:
            context.update()
        runtime_data.frame_counter += 1
        _dpg.render_dearpygui_frame()
    _dpg.destroy_context()
