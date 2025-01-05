from typing import Any as _Any


def time_invalid(o: _Any) -> bool:
    return not isinstance(o, int)


def speed_invalid(o: _Any) -> bool:
    return not isinstance(o, int | float) or o < 0


def acceleration_invalid(o: _Any) -> bool:
    return not isinstance(o, int | float)


def mileage_invalid(o: _Any) -> bool:
    return not isinstance(o, int | float)


def latitude_invalid(o: _Any) -> bool:
    return not isinstance(o, int | float) or not -90 < o < 90


def longitude_invalid(o: _Any) -> bool:
    return not isinstance(o, int | float) or not -180 < o < 180


def latency_invalid(o: _Any) -> bool:
    return not isinstance(o, int | float)
