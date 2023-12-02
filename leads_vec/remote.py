from collections import deque
from json import loads

from dearpygui import dearpygui as dpg
from numpy import trapz

from leads.comm import *
from leads_dashboard import *


class CustomCallback(Callback):
    speed_seq: deque = deque(maxlen=1000)

    def on_initialize(self, service: Service):
        print("Server started")

    def on_fail(self, service: Service, error: Exception):
        print(error)

    def on_receive(self, service: Service, msg: bytes):
        data = loads(msg.decode())
        front_wheel_speed = data["front_wheel_speed"]
        self.speed_seq.append(front_wheel_speed)
        dpg.set_value("speed", f"FWS: {int(front_wheel_speed)} Km / H")
        dpg.set_value("displacement", f"{int(trapz(self.speed_seq, dx=.001))} Km")
        dpg.set_value("speed_seq", list(self.speed_seq))


def render():
    dpg.bind_item_font(dpg.add_text("", tag="speed"), H2)
    dpg.bind_item_font(dpg.add_text("", tag="displacement"), H2)
    dpg.add_simple_plot(label="Speed Trend", tag="speed_seq", height=300)


def remote() -> int:
    start_comm_server(render, create_server(callback=CustomCallback()))
    return 0


if __name__ == '__main__':
    remote()
