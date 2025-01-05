from json import dumps as _dumps
from time import time as _time
from typing import override as _override, Any as _Any

from numpy import radians as _radians, degrees as _degrees, cos as _cos, sqrt as _sqrt


class Serializable(object):
    def to_dict(self) -> dict[str, _Any]:
        return {n: v for n in dir(self) if (v := getattr(self, n)) is not None and not callable(v) and not n.startswith(
            "_")}


class DataContainer(Serializable):
    def __init__(self,
                 voltage: float = 0,
                 speed: float = 0,
                 front_wheel_speed: float = 0,
                 rear_wheel_speed: float = 0,
                 yaw: float = 0,
                 pitch: float = 0,
                 roll: float = 0,
                 forward_acceleration: float = 0,
                 lateral_acceleration: float = 0,
                 vertical_acceleration: float = 0,
                 front_proximity: float = -1,
                 left_proximity: float = -1,
                 right_proximity: float = -1,
                 rear_proximity: float = -1,
                 mileage: float = 0,
                 gps_valid: bool = False,
                 gps_ground_speed: float = 0,
                 latitude: float = 0,
                 longitude: float = 0,
                 steering_position: float = 0,
                 throttle: float = 0,
                 brake: float = 0,
                 **kwargs) -> None:
        self._time_stamp: int = int(_time() * 1000)
        self.voltage: float = voltage
        self.speed: float = speed
        self.front_wheel_speed: float = front_wheel_speed
        self.rear_wheel_speed: float = rear_wheel_speed
        self.yaw: float = yaw
        self.pitch: float = pitch
        self.roll: float = roll
        self.forward_acceleration: float = forward_acceleration
        self.lateral_acceleration: float = lateral_acceleration
        self.vertical_acceleration: float = vertical_acceleration
        self.front_proximity: float = front_proximity
        self.left_proximity: float = left_proximity
        self.right_proximity: float = right_proximity
        self.rear_proximity: float = rear_proximity
        self.mileage: float = mileage
        self.gps_valid: bool = gps_valid
        self.gps_ground_speed: float = gps_ground_speed
        self.latitude: float = latitude
        self.longitude: float = longitude

        self.steering_position: float = steering_position
        self.throttle: float = throttle
        self.brake: float = brake

        for k, v in kwargs.items():
            setattr(self, k, v)

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
    def to_dict(self) -> dict[str, _Any]:
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


class VisualDataContainer(DataContainer):
    def __init__(self,
                 voltage: float = 0,
                 speed: float = 0,
                 front_wheel_speed: float = 0,
                 rear_wheel_speed: float = 0,
                 yaw: float = 0,
                 pitch: float = 0,
                 roll: float = 0,
                 forward_acceleration: float = 0,
                 lateral_acceleration: float = 0,
                 vertical_acceleration: float = 0,
                 front_proximity: float = -1,
                 left_proximity: float = -1,
                 right_proximity: float = -1,
                 rear_proximity: float = -1,
                 mileage: float = 0,
                 gps_valid: bool = False,
                 gps_ground_speed: float = 0,
                 latitude: float = 0,
                 longitude: float = 0,
                 steering_position: float = 0,
                 throttle: float = 0,
                 brake: float = 0,
                 front_view_base64: str = "",
                 front_view_latency: int = 0,
                 left_view_base64: str = "",
                 left_view_latency: int = 0,
                 right_view_base64: str = "",
                 right_view_latency: int = 0,
                 rear_view_base64: str = "",
                 rear_view_latency: int = 0,
                 **kwargs) -> None:
        super().__init__(voltage, speed, front_wheel_speed, rear_wheel_speed, yaw, pitch, roll, forward_acceleration,
                         lateral_acceleration, vertical_acceleration, front_proximity, left_proximity, right_proximity,
                         rear_proximity, mileage, gps_valid, gps_ground_speed, latitude, longitude, steering_position,
                         throttle, brake, **kwargs)
        self.front_view_base64: str = front_view_base64
        self.front_view_latency: int = front_view_latency
        self.left_view_base64: str = left_view_base64
        self.left_view_latency: int = left_view_latency
        self.right_view_base64: str = right_view_base64
        self.right_view_latency: int = right_view_latency
        self.rear_view_base64: str = rear_view_base64
        self.rear_view_latency: int = rear_view_latency


def dlat2meters(dlat: float) -> float:
    return dlat * 111320


def meters2dlat(meters: float) -> float:
    return meters / 111320


def dlon2meters(dlon: float, lat: float) -> float:
    return _radians(6378137 * dlon * _cos(_radians(lat)))


def meters2dlon(meters: float, lat: float) -> float:
    return _degrees(meters / 6378137 / _cos(_radians(lat)))


def distance_between(lat_0: float, lon_0: float, lat: float, lon: float) -> float:
    """
    Calculate the distance between two locations on the Earth.
    :param lat_0: the latitude of the first location
    :param lon_0: the longitude of the first location
    :param lat: the latitude of the second location
    :param lon: the longitude of the second location
    :return:
    """
    return _sqrt(dlon2meters(lon - lon_0, .5 * (lat_0 + lat)) ** 2 + dlat2meters(lat - lat_0) ** 2)


def format_duration(duration: float) -> str:
    """
    Wrap the duration into a formatted string.
    :param duration: the duration in seconds
    :return: the formatted string
    """
    return f"{(duration := int(duration)) // 60} MIN {duration % 60} SEC"
