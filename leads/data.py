from json import dumps as _dumps
from time import time as _time
from typing import override as _override, Any as _Any


class Serializable(object):
    def to_dict(self) -> dict[str, _Any]:
        return {n: v for n in dir(self) if not n.startswith("_") and not callable(v := getattr(self, n))}


class DataContainer(Serializable):
    def __init__(self,
                 voltage: float = 0,
                 speed: float = 0,
                 front_wheel_speed: float = 0,
                 rear_wheel_speed: float = 0,
                 forward_acceleration: float = 0,
                 lateral_acceleration: float = 0,
                 mileage: float = 0,
                 gps_valid: bool = False,
                 gps_ground_speed: float = 0,
                 latitude: float = 0,
                 longitude: float = 0) -> None:
        self._time_stamp: int = int(_time() * 1000)
        self.voltage: float = voltage
        self.speed: float = speed
        self.front_wheel_speed: float = front_wheel_speed
        self.rear_wheel_speed: float = rear_wheel_speed
        self.forward_acceleration: float = forward_acceleration
        self.lateral_acceleration: float = lateral_acceleration
        self.mileage: float = mileage
        self.gps_valid: bool = gps_valid
        self.gps_ground_speed: float = gps_ground_speed
        self.latitude: float = latitude
        self.longitude: float = longitude

        self.throttle: float = 0
        self.brake: float = 0

    @_override
    def __str__(self) -> str:
        return _dumps(self.to_dict())

    def reset_time_stamp(self) -> None:
        """
        Reset the data's time stamp to now.
        """
        self._time_stamp = int(_time() * 1000)

    def time_stamp(self) -> int:
        """
        Get the data's time stamp.
        :return: the time stamp (ms)
        """
        return self._time_stamp

    @_override
    def to_dict(self) -> dict:
        """
        Convert the data into a dictionary.
        :return: a dictionary that contains all custom attributes of the container
        """
        (r := super().to_dict())["t"] = self._time_stamp
        return r

    def encode(self) -> bytes:
        """
        Encode the data into bytes for network transaction purposes.
        :return: JSON in bytes
        """
        return str(self).encode()
