from leads.comm.server import *
from leads.comm.prototype import Service


class CustomCallback(Callback):
    def on_receive(self, service: Service, msg: bytes):
        print(msg)

    def on_disconnect(self, service: Service):
        print("Disconnected")


start_server(parallel=True, target=create_server(callback=CustomCallback()))
