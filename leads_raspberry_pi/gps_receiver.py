from leads import Sensor as _Sensor, T


class GPSReceiver(_Sensor[[float, float]]):
    def read(self) -> T:
        return [.0, .0]
