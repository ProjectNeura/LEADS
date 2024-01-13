from serial import Serial as _Serial

from leads import Controller as _Controller


class ArduinoNano(_Controller):
    def __init__(self, port: str = "/dev/ttyUSB1", baud_rate: int = 9600) -> None:
        super().__init__()
        self._port: str = port
        self._baud_rate: int = baud_rate
        self._serial: _Serial | None = None

    async def initialize(self, *parent_tags: str) -> None:
        self._serial = _Serial(self._port, self._baud_rate, timeout=1)

    def read(self) -> bytes:
        return self._serial.read()

    def write(self, payload: bytes) -> None:
        self._serial.write(payload)
