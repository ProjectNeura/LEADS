from leads import ShadowDevice as _ShadowDevice


class GPSReceiver(_ShadowDevice):
    def loop(self) -> None:
        pass

    def read(self) -> [float, float]:
        return [0, 0]
