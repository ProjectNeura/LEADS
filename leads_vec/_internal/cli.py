from leads import *
from leads_dashboard import *
from dearpygui import dearpygui as dpg


def render():
    with dpg.table(header_row=False):
        dpg.add_table_column()
        dpg.add_table_column()
        dpg.add_table_column()
        with dpg.table_row():
            dpg.bind_item_font(dpg.add_text("", tag="time"), BODY2)
            dpg.bind_item_font(dpg.add_text("", tag="speed"), H1)


def main(main_controller: Controller) -> int:
    context = Leads[DefaultDataContainer]()
    runtime_data = RuntimeData()

    class CustomListener(EventListener):
        def on_update(self, e: UpdateEvent):
            dpg.set_value("time", f"RUN FOR {runtime_data.frame_counter / 3000} MIN")
            dpg.set_value("speed", f"{context.data().wheel_speed} KM/H")

    context.set_event_listener(CustomListener())

    start(render, context, main_controller, runtime_data)

    return 0
