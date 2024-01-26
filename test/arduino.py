from leads.comm import *
from leads_arduino import *


class CustomCallback(Callback):
    def on_receive(self, service: Service, msg: bytes) -> None:
        print(msg)

    def on_connect(self, service: Service, connection: ConnectionBase) -> None:
        print("Connected")

    def on_fail(self, service: Service, error: Exception) -> None:
        print(error)


controller = ArduinoMicro("COM3", CustomCallback())
controller.initialize()
controller.close()
