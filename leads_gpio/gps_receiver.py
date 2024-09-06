from typing import override as _override, Literal as _Literal

from pynmea2 import parse as _parse
from pynmea2.types.talker import TalkerSentence as _TalkerSentence
from serial import Serial as _Serial

from leads import Device as _Device, SFT as _SFT
from leads.comm import Entity as _Entity, Callback as _Callback, Service as _Service
from leads_comm_serial import SerialConnection as _SerialConnection, AutoIdentity as _AutoIdentity, SerialConnection


class NMEAGPSReceiver(_Device, _Entity, _AutoIdentity):
    """
    Supports:
    - Any USB (serial) GPS receiver with NMEA 0183 output
    """

    def __init__(self, port: str | _Literal["auto"], baud_rate: int = 9600) -> None:
        _Device.__init__(self, port)
        _Entity.__init__(self, -1, _NMEAGPSCallback(self))
        _AutoIdentity.__init__(self, port == "auto", separator=b"\n")
        self._serial: _Serial = _Serial()
        self._serial.baudrate = baud_rate
        self._connection: _SerialConnection | None = None
        self._serial.port = self.suggest_next_port() if port == "auto" else port
        self._valid: bool = False
        self._ground_speed: float = 0
        self._latitude: float = 0
        self._longitude: float = 0
        self._quality: int = 0
        self._num_satellites: int = 0

    @_override
    def port(self) -> str:
        return self._serial.port

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self.start(True)

    @_override
    def check_identity(self, connection: SerialConnection) -> bool:
        try:
            _parse(connection.receive().decode())
            return True
        except ValueError:
            return False

    @_override
    def update(self, data: _TalkerSentence) -> None:
        if hasattr(data, "latitude"):
            self._latitude = float(data.latitude)
        if hasattr(data, "longitude"):
            self._longitude = float(data.longitude)
        if hasattr(data, "is_valid"):
            if (v := data.is_valid) and not self._valid:
                _SFT.recover(self)
            elif not v and self._valid:
                _SFT.fail(self, "No fix")
            self._valid = v
        if NMEAGPSReceiver._has_field(data.fields, "spd_over_grnd", 6):
            self._ground_speed = float(ground_speed) * 1.852 if (ground_speed := data.data[6]) else 0
        if NMEAGPSReceiver._has_field(data.fields, "gps_qual", 5):
            self._quality = int(data.data[5])
        if NMEAGPSReceiver._has_field(data.fields, "num_sats", 6):
            self._num_satellites = int(data.data[6])

    @_override
    def read(self) -> tuple[bool, float, float, float, int, int]:
        """
        :return: (validity, ground speed, latitude, longitude, quality, num of satellites)
        """
        return self._valid, self._ground_speed, self._latitude, self._longitude, self._quality, self._num_satellites

    @_override
    def run(self) -> None:
        self._callback.on_initialize(self)
        self._connection = self.establish_connection(self._serial)
        self._callback.on_connect(self, self._connection)
        self._stage(self._connection)

    @_override
    def close(self) -> None:
        if self._connection:
            self._connection.close()

    @staticmethod
    def _has_field(fields: tuple[tuple[str, str, ...], ...], target_field: str, at: int) -> bool:
        return len(fields) > at and fields[at][1] == target_field


class _NMEAGPSCallback(_Callback):
    def __init__(self, receiver: NMEAGPSReceiver) -> None:
        super().__init__()
        self._receiver: _Device = receiver

    @_override
    def on_connect(self, service: _Service, connection: _SerialConnection) -> None:
        _SFT.fail(self._receiver, "No fix")

    @_override
    def on_receive(self, service: _Service, msg: bytes) -> None:
        self.super(service=service, msg=msg)
        self._receiver.update(_parse(msg.decode()))

    @_override
    def on_fail(self, service: _Service, error: Exception) -> None:
        self.super(service=service, error=error)
        _SFT.fail(self._receiver, error)
