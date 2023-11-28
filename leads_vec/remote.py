from collections import deque
from json import loads

from dearpygui import dearpygui as dpg

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
        dpg.set_value("speed", f"FWS: {front_wheel_speed} Km / H")
        dpg.set_value("speed_seq", list(self.speed_seq))


def render():
    dpg.add_text("", tag="speed")
    dpg.add_simple_plot(label="Speed", tag="speed_seq", height=300)


def remote() -> int:
    start_comm_server(render, create_server(callback=CustomCallback()))
    return 0


if __name__ == '__main__':
    remote()
