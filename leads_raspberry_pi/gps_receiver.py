from typing import override as _override

from leads import ShadowDevice as _ShadowDevice


class GPSReceiver(_ShadowDevice):
    @_override
    def loop(self) -> None:
        pass

    @_override
    def read(self) -> [float, float]:
        return [0, 0]
