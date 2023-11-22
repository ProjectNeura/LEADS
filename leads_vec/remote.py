from dearpygui import dearpygui as dpg

from leads.comm import *
from leads_dashboard import *


class CustomCallback(Callback):
    def on_receive(self, service: Service, msg: bytes):
        dpg.set_value("current", msg.decode())


if __name__ == '__main__':
    def render():
        dpg.add_text("", tag="current")


    start_comm_server(render, create_server(callback=CustomCallback()))
