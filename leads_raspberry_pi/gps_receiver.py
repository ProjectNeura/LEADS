from typing import override as _override

from gps import gps as _gps

from leads import ShadowDevice as _ShadowDevice


class GPSReceiver(_ShadowDevice):
    def __init__(self, port: str) -> None:
        super().__init__(port)
        self._gpsd: _gps | None = None
        self._latitude: float = 0
        self._longitude: float = 0

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self._gpsd = _gps()

    def require_gpsd(self) -> _gps:
        if self._gpsd:
            return self._gpsd
        raise RuntimeError("Not initialized")

    @_override
    def loop(self) -> None:
        nx = self.require_gpsd().next()
        if nx["class"] == "TPV":
            self._latitude = float(nx["lat"])
            self._longitude = float(nx["lon"])

    @_override
    def read(self) -> [float, float]:
        """
        :return: [latitude, longitude]
        """
        return self._latitude, self._longitude
