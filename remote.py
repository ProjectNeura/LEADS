from leads.comm import *


class RemoteDisplay(Callback):
    def on_receive(self, service: Service, msg: bytes):
        print(msg)


create_server()
