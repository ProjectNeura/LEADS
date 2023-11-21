from leads.comm.client import *
from leads.comm.prototype import Service, Connection


class CustomCallback(Callback):
    def on_connect(self, service: Service, connection: Connection):
        connection.disconnect()


start_client("127.0.0.1", create_client(callback=CustomCallback()))
