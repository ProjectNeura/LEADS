from leads import *
from time import sleep
from random import randint
from dearpygui import dearpygui as dpg


dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(label="LEADS", no_title_bar=True, no_scrollbar=True, menubar=False, no_close=True):
    dpg.add_text("", tag="time", )
    dpg.add_text("", tag="speed")

dpg.show_viewport()

context = Leads[DefaultDataContainer]()
frame_counter = 0


class CustomListener(EventListener):
    def on_update(self, e: UpdateEvent):
        dpg.set_value("time", f"RUN FOR {frame_counter / 3000} MIN")
        dpg.set_value("speed", f"{context.data().wheel_speed} KM/H")


context.set_event_listener(CustomListener())

while dpg.is_dearpygui_running():
    sleep(.02)
    context.push(DefaultDataContainer(wheel_speed=randint(1, 100)))
    if frame_counter % 30 == 0:
        context.update()
    frame_counter += 1
    dpg.render_dearpygui_frame()

dpg.destroy_context()
