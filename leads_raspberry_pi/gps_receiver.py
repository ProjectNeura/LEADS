from leads import ShadowDevice as _ShadowDevice


class GPSReceiver(_ShadowDevice):
    def read(self) -> [float, float]:
        return [.0, .0]
