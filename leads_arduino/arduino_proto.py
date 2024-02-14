from serial import Serial as _Serial

from leads import Controller as _Controller
from leads.comm import Entity as _Entity, Callback as _Callback
from leads_comm_serial import SerialConnection as _SerialConnection


class ArduinoProto(_Controller, _Entity):
    def __init__(self, port: str, callback: _Callback, baud_rate: int = 9600) -> None:
        _Controller.__init__(self)
        _Entity.__init__(self, -1, callback)
        self._serial: _Serial = _Serial()
        self._serial.port = port
        self._serial.baudrate = baud_rate
        self._connection: _SerialConnection | None = None

    def port(self) -> str:
        return self._serial.port

    def initialize(self, *parent_tags: str) -> None:
        self.start(True)
        super().initialize(*parent_tags)

    def run(self) -> None:
        self.callback.on_initialize(self)
        self._serial.open()
        self.callback.on_connect(self, connection := _SerialConnection(self, self._serial, self._serial.port))
        self._connection = connection
        self._stage(connection)

    def write(self, payload: bytes) -> None:
        if not self._connection:
            raise IOError("Target must be connected to perform this operation")
        self._connection.send(payload)

    def kill(self) -> None:
        if self._connection:
            self._connection.close()

    def close(self) -> None:
        self.kill()
