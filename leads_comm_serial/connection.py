from time import time as _time
from typing import override as _override, Literal as _Literal, Self as _Self

from serial import Serial as _Serial

from leads.comm import ConnectionBase as _ConnectionBase


class SerialConnection(_ConnectionBase):
    def __init__(self, serial: _Serial, remainder: bytes = b"", separator: bytes = b";") -> None:
        super().__init__(remainder, separator)
        self._serial: _Serial = serial

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
        start = _time()
        try:
            msg = chunk = b""
            while not ((t_o := self._serial.timeout) and _time() - start > t_o) and self._separator not in chunk:
                msg += (chunk := self._require_open_serial().read(chunk_size))
            return self.with_remainder(msg)
        except IOError:
            return

    @_override
    def send(self, msg: bytes | _Literal[b"disconnect"]) -> None:
        self._require_open_serial().write(msg + self._separator)

    @_override
    def close(self) -> None:
        self.disconnect()
        self._require_open_serial(False).close()

    def suspect(self, timeout: int = 1) -> _Self:
        self._serial.timeout = timeout
        return self

    def trust(self) -> _Self:
        self._serial.timeout = None
        return self
