from typing import override as _override

from pynmea2 import parse as _parse
from pynmea2.types.talker import TalkerSentence as _TalkerSentence, VTG as _VTG
from serial import Serial as _Serial

from leads import Device as _Device, SFT as _SFT
from leads.comm import Entity as _Entity, Callback as _Callback, Service as _Service
from leads_comm_serial import SerialConnection as _SerialConnection


class _GPSCallback(_Callback):
    def __init__(self, receiver: _Device) -> None:
        self.receiver: _Device = receiver

    @_override
    def on_receive(self, service: _Service, msg: bytes) -> None:
        assert isinstance(service, NMEAGPSReceiver)
        self.receiver.update(_parse(msg.decode()))

    @_override
    def on_fail(self, service: _Service, error: Exception) -> None:
        assert isinstance(service, NMEAGPSReceiver)
        _SFT.fail(service, error)


class NMEAGPSReceiver(_Device, _Entity):
    """
    Supports:
    - Any USB (serial) GPS receiver with NMEA 0183 output
    """
    def __init__(self, port: str, baud_rate: int = 9600) -> None:
        _Device.__init__(self, port)
        _Entity.__init__(self, -1, _GPSCallback(self))
        self._serial: _Serial = _Serial()
        self._serial.port = port
        self._serial.baudrate = baud_rate
        self._connection: _SerialConnection | None = None
        self._latitude: float = 0
        self._longitude: float = 0
        self._ground_speed: float = 0
        self._valid: bool = True

    @_override
    def port(self) -> str:
        return self._serial.port

    @_override
    def initialize(self, *parent_tags: str) -> None:
        self.start(True)
        super().initialize(*parent_tags)

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
        if isinstance(data, _VTG):
            self._ground_speed = float(ground_speed) if (ground_speed := data.data[6]) else 0

    @_override
    def read(self) -> [bool, float, float]:
        """
        :return: [validity, latitude, longitude]
        """
        return self._valid, self._latitude, self._longitude

    @_override
    def run(self) -> None:
        self.callback.on_initialize(self)
        self._serial.open()
        self.callback.on_connect(self, connection := _SerialConnection(self, self._serial, self._serial.port,
                                                                       separator=b"\n"))
        self._connection = connection
        self._stage(connection)

    @_override
    def kill(self) -> None:
        if self._connection:
            self._connection.close()

    @_override
    def close(self) -> None:
        self.kill()
