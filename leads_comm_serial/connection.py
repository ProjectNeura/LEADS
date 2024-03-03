from typing import override as _override

from serial import Serial as _Serial

from leads.comm import ConnectionBase as _Connection, Service as _Service


class SerialConnection(_Connection):
    def __init__(self,
                 service: _Service,
                 serial: _Serial,
                 port: str,
                 remainder: bytes = b"",
                 separator: bytes = b";") -> None:
        super().__init__(service, remainder, separator)
        self._serial: _Serial = serial
        self._port: str = port

    @_override
    def closed(self) -> bool:
        return self._serial.closed

    def _require_open_serial(self, mandatory: bool = True) -> _Serial:
        if mandatory and self.closed():
            raise IOError("An open serial is required")
        return self._serial

    @_override
    def receive(self, chunk_size: int = 1) -> bytes | None:
        if self._remainder != b"":
            return self.use_remainder()
        try:
            msg = chunk = b""
            while self._separator not in chunk:
                msg += (chunk := self._require_open_serial().read(chunk_size))
            return self.with_remainder(msg)
        except IOError:
            return

    @_override
    def send(self, msg: bytes) -> None:
        self._require_open_serial().write(msg + self._separator)
        if msg == b"disconnect":
            self.close()

    @_override
    def close(self) -> None:
        self._require_open_serial(False).close()
