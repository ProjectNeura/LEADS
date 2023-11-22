from leads.comm.prototype import Service
from leads.comm.server import *


class CustomCallback(Callback):
    def on_fail(self, service: Service, error: Exception):
        print(error)

    def on_receive(self, service: Service, msg: bytes):
        print(msg)

    def on_disconnect(self, service: Service):
        print("Disconnected")


start_server(parallel=True, target=create_server(callback=CustomCallback()))
