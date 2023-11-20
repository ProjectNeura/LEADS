from leads import *
from leads_dashboard import *
from datetime import datetime
from dearpygui import dearpygui as dpg

from ..__version__ import __version__


def render():
    with dpg.table(header_row=False):
        dpg.add_table_column()
        dpg.add_table_column()
        dpg.add_table_column()
        with dpg.table_row():
            dpg.bind_item_font(dpg.add_text("", tag="time"), BODY2)
            dpg.bind_item_font(dpg.add_text("", tag="speed"), H1)


def main(main_controller: Controller) -> int:
    context = Leads[SRWDataContainer]()
    rd = RuntimeData()

    class CustomListener(EventListener):
        def on_update(self, e: UpdateEvent):
            d = context.data()
            dpg.set_value("time", f"VERSION {__version__.upper()}\n\n"
                                  f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                  f"{rd.frame_counter // 3000} MIN {(rd.frame_counter % 3000) // 50} SEC")
            dpg.set_value("speed", f"{min(d.left_front_wheel_speed, d.right_front_wheel_speed)} KM/H")

    context.set_event_listener(CustomListener())

    start(render, context, main_controller, rd)

    return 0
