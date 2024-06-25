from typing import Any as _Any

from leads.data import dlat2meters, dlon2meters
from .._computational import sqrt as _sqrt


def time_invalid(o: _Any) -> bool:
    return not isinstance(o, int)


def speed_invalid(o: _Any) -> bool:
    return not isinstance(o, int | float) or o != o or o < 0


def acceleration_invalid(o: _Any) -> bool:
    return not isinstance(o, int | float) or o != o


def mileage_invalid(o: _Any) -> bool:
    return not isinstance(o, int | float) or o != o


def latitude_invalid(o: _Any) -> bool:
    return not isinstance(o, int | float) or o != o or not -90 < o < 90


def longitude_invalid(o: _Any) -> bool:
    return not isinstance(o, int | float) or o != o or not -180 < o < 180


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
