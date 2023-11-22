from leads.comm.client import *
from leads.comm.prototype import Service, Connection


class CustomCallback(Callback):
    def on_fail(self, service: Service, error: Exception):
        print(error)

    def on_receive(self, service: Service, msg: bytes):
        print(msg)

    def on_connect(self, service: Service, connection: Connection):
        print("Connected")
        connection.send(b"ABC")
        connection.send(b"DEF")


start_client("127.0.0.1", create_client(callback=CustomCallback()))
