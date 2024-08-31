from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod

from serial import Serial as _Serial, SerialException as _SerialException
from serial.tools.list_ports import comports as _comports

from leads.comm import Service as _Service
from leads_comm_serial.connection import SerialConnection


class AutoIdentity(object, metaclass=_ABCMeta):
    def __init__(self, retry: bool = False) -> None:
        self._retry: bool = retry
        self._tried_ports: list[str] = []

    def suggest_next_port(self, tried_port: str | None = None) -> str | None:
        if tried_port:
            self._tried_ports.append(tried_port)
        for port, _, __ in _comports():
            if port not in self._tried_ports:
                return port

    @_abstractmethod
    def check_identity(self, connection: SerialConnection) -> bool:
        raise NotImplementedError

    def establish_connection(self, service: _Service, serial: _Serial, remainder: bytes = b"",
                             separator: bytes = b";") -> SerialConnection:
        try:
            if not serial.port:
                raise ConnectionError("No available port")
            serial.open()
            if self.check_identity(connection := SerialConnection(service, serial, serial.port, remainder, separator)):
                return connection
            raise ValueError("Unexpected identity")
        except (_SerialException, ValueError) as e:
            if not self._retry:
                raise ConnectionError(f"Unable to establish connection due to {repr(e)}")
            serial.port = self.suggest_next_port(serial.port)
            return self.establish_connection(service, serial)
