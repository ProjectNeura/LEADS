from typing import override as _override, Literal as _Literal

from serial import Serial as _Serial
from serial.serialutil import SerialException
from serial.tools.list_ports import comports as _comports

from leads import Controller as _Controller, SFT as _SFT, L as _L
from leads.comm import Entity as _Entity, Callback as _Callback, Service as _Service
from leads_comm_serial import SerialConnection as _SerialConnection


class ArduinoProto(_Controller, _Entity):
    """
    Supports:
    - Any arduino connected through a USB (serial) port
    """

    def __init__(self, port: str | _Literal["auto"], baud_rate: int = 9600) -> None:
        _Controller.__init__(self)
        _Entity.__init__(self, -1, _ArduinoCallback(self))
        self._serial: _Serial = _Serial()
        self._port_list: list[str] | None = [p[0] for p in _comports()] if port == "auto" else None
        self._serial.port = self._port_list.pop(0) if port == "auto" else port
        self._serial.baudrate = baud_rate
        self._connection: _SerialConnection | None = None

    @_override
    def port(self) -> str:
        return self._serial.port

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self.start(True)

    @_override
    def update(self, data: str) -> None:
        for d in self.devices():
            d.update(data)

    @_override
    def run(self) -> None:
        try:
            self._callback.on_initialize(self)
            self._serial.open()
            self._connection.send(b"ic")
            msg = self._connection.receive()
            if msg is None or not msg.startswith(self.tag().encode()):
                raise ConnectionError("Unmatched identity")
            self._callback.on_connect(self, connection := _SerialConnection(self, self._serial, self._serial.port))
            self._connection = connection
            self._stage(connection)
        except (SerialException, ConnectionError):
            if not self._port_list:
                raise ConnectionError("Connection failed")
            self._serial.port = self._port_list.pop(0)
            self.run()

    @_override
    def write(self, payload: bytes) -> None:
        if not self._connection:
            raise IOError("Target must be connected to perform this operation")
        self._connection.send(payload)

    @_override
    def close(self) -> None:
        if self._connection:
            self._connection.close()


class _ArduinoCallback(_Callback):
    def __init__(self, arduino: ArduinoProto) -> None:
        super().__init__()
        self._arduino: ArduinoProto = arduino

    @_override
    def on_receive(self, service: _Service, msg: bytes) -> None:
        self.super(service=service, msg=msg)
        try:
            self._arduino.update(msg.decode())
        except UnicodeDecodeError:
            _L.debug(f"Discarding this message: {msg}")

    @_override
    def on_fail(self, service: _Service, error: Exception) -> None:
        self.super(service=service, error=error)
        _SFT.fail(self._arduino, error)
