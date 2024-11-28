from typing import Literal as _Literal, override as _override

from serial import Serial as _Serial

from leads import require_config as _require_config, Device as _Device, L as _L
from leads.comm import Entity as _Entity, Callback as _Callback, Service as _Service, ConnectionBase as _ConnectionBase
from leads_comm_serial.connection import SerialConnection
from leads_comm_serial.identity import AutoIdentity


class SOBD(_Device, _Entity, AutoIdentity):
    def __init__(self, port: str | _Literal["auto"], baud_rate: int = 9600, password: str = "") -> None:
        _Device.__init__(self)
        _Entity.__init__(self, -1, _SOBDCallback(self))
        AutoIdentity.__init__(self, port == "auto")
        self._serial: _Serial = _Serial()
        self._serial.baudrate = baud_rate
        self._connection: SerialConnection | None = None
        self._serial.port = self.suggest_next_port() if port == "auto" else port
        self._password: str = password
        self._locked: bool = password != ""

    @_override
    def port(self) -> str:
        return self._serial.port

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self.start(True)

    @_override
    def update(self, data: str) -> None:
        if data.startswith("pwd="):
            if data[4:] != self._password:
                self.close()
            else:
                self._locked = False
        if self._locked:
            return
        if data.startswith("dbl="):
            _require_config().w_debug_level = data[4:].upper()
        else:
            self.write("\n".join(_L.history_messages()).encode())

    @_override
    def check_identity(self, connection: SerialConnection) -> bool:
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


class _SOBDCallback(_Callback):
    def __init__(self, sobd: SOBD) -> None:
        super().__init__()
        self._sobd: SOBD = sobd

    @_override
    def on_connect(self, service: _Service, connection: _ConnectionBase) -> None:
        _L.debug(f"SOBD connected on {self._sobd.port()}")


    @_override
    def on_receive(self, service: _Service, msg: bytes) -> None:
        self.super(service=service, msg=msg)
        try:
            self._sobd.update(msg.decode())
        except UnicodeDecodeError:
            _L.debug(f"Discarding this message: {msg}")
