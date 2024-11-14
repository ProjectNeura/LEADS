from typing import Literal as _Literal, override as _override

from serial import Serial as _Serial

from leads.comm import Entity, Callback, Service
from leads.dt.device import Device
from leads.logger import L
from leads_comm_serial import SerialConnection as _SerialConnection, AutoIdentity as _AutoIdentity


class SOBD(Device, Entity, _AutoIdentity):
    def __init__(self, port: str | _Literal["auto"], baud_rate: int = 9600) -> None:
        Device.__init__(self)
        Entity.__init__(self, -1, _SOBDCallback(self))
        _AutoIdentity.__init__(self, port == "auto")
        self._serial: _Serial = _Serial()
        self._serial.baudrate = baud_rate
        self._connection: _SerialConnection | None = None
        self._serial.port = self.suggest_next_port() if port == "auto" else port

    @_override
    def port(self) -> str:
        return self._serial.port

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self.start(True)

    @_override
    def update(self, data: str) -> None:
        # todo
        pass

    @_override
    def check_identity(self, connection: _SerialConnection) -> bool:
        connection.send(b"ic")
        return (msg := connection.receive()) and msg.startswith(self.tag().encode())

    @_override
    def run(self) -> None:
        self._callback.on_initialize(self)
        self._connection = self.establish_connection(self._serial)
        self._callback.on_connect(self, self._connection)
        self._stage(self._connection)

    @_override
    def write(self, payload: bytes) -> None:
        if not self._connection:
            raise IOError("Target must be connected to perform this operation")
        self._connection.send(payload)

    @_override
    def close(self) -> None:
        if self._connection:
            self._connection.close()


class _SOBDCallback(Callback):
    def __init__(self, sobd: SOBD) -> None:
        super().__init__()
        self._sobd: SOBD = sobd

    @_override
    def on_receive(self, service: Service, msg: bytes) -> None:
        self.super(service=service, msg=msg)
        try:
            self._sobd.update(msg.decode())
        except UnicodeDecodeError:
            L.debug(f"Discarding this message: {msg}")
