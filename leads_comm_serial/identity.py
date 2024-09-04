from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from threading import Lock as _Lock

from serial import Serial as _Serial, SerialException as _SerialException
from serial.tools.list_ports import comports as _comports

from leads_comm_serial.connection import SerialConnection

_available_ports: list[str] = [_p for _p, _, __ in _comports()]


class AutoIdentity(object, metaclass=_ABCMeta):
    def __init__(self, retry: bool = False, remainder: bytes = b"", seperator: bytes = b";") -> None:
        self._retry: bool = retry
        self._remainder: bytes = remainder
        self._seperator: bytes = seperator
        self._tried_ports: list[str] = []
        _instances[self] = None

    def meta(self) -> tuple[bool, bytes, bytes]:
        return self._retry, self._remainder, self._seperator

    def suggest_next_port(self, tried_port: str | None = None) -> str | None:
        if tried_port:
            self._tried_ports.append(tried_port)
        for port in _available_ports:
            if port not in self._tried_ports:
                return port

    @_abstractmethod
    def check_identity(self, connection: SerialConnection) -> bool:
        raise NotImplementedError

    def establish_connection(self, serial: _Serial) -> SerialConnection:
        _detect_ports()
        try:
            if port := _instances[self]:
                serial.port = port
                self._retry = False
            elif not serial.port:
                raise ConnectionError("No available port")
            elif serial.port not in _available_ports:
                raise ValueError("Port taken")
            serial.open()
            connection = SerialConnection(serial).suspect()
            if port or self.check_identity(connection):
                return connection.trust()
            for instance in _instances.keys():
                if instance.check_identity(connection):
                    _instances[instance] = serial.port
            raise ValueError("Unexpected identity")
        except (_SerialException, ValueError) as e:
            serial.close()
            if not self._retry:
                raise ConnectionError(f"Unable to establish connection due to {repr(e)}")
            serial.port = self.suggest_next_port(serial.port)
            return self.establish_connection(serial)


_instances: dict[AutoIdentity, str | None] = {}
_ports_detected: bool = False
_ports_lock: _Lock = _Lock()


def _detect_ports() -> None:
    global _ports_detected
    _ports_lock.acquire()
    try:
        if _ports_detected:
            return
        for port in tuple(_available_ports):
            serial = _Serial()
            serial.port = port
            serial.open()
            connection = SerialConnection(serial).suspect()
            for instance in _instances.keys():
                connection._separator = instance.meta()[2]
                if instance.check_identity(connection):
                    _instances[instance] = port
                    _available_ports.remove(port)
                    break
            serial.close()
    finally:
        _ports_detected = True
        _ports_lock.release()
