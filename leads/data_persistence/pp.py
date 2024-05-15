from datetime import datetime as _datetime
from typing import Any as _Any, Callable as _Callable

from matplotlib.pyplot import scatter as _scatter, show as _show, title as _title, colorbar as _colorbar

from leads.data import dlat2meters, dlon2meters
from leads.data_persistence.core import Dataset


class PostProcessor(object):
    def __init__(self, dataset: Dataset) -> None:
        self._dataset: Dataset = dataset

        # baking variables
        self._read_rows: int = 0
        self._valid_rows: int = 0
        self._invalid_rows: list[int] = []
        self._start_time: float | None = None
        self._end_time: float | None = None
        self._min_speed: float | None = None
        self._max_speed: float | None = None
        self._avg_speed: float | None = None
        self._gps_valid_count: int = 0
        self._gps_invalid_rows: list[int] = []
        self._min_lat: float | None = None
        self._min_lon: float | None = None

        # processor variables
        self._laps: list[tuple[int, int]] = []

        # unit variables (not reusable)
        self._t: float | None = None
        self._lap_start: int | None = None
        self._lap_start_time: float | None = None
        self._lap_end_time: float | None = None
        self._x: list[float] = []
        self._y: list[float] = []
        self._d: list[float] = []

    @staticmethod
    def time_invalid(o: _Any) -> bool:
        return not isinstance(o, float) and not isinstance(o, int)

    @staticmethod
    def speed_invalid(o: _Any) -> bool:
        return not isinstance(o, float) or o < 0 or o != o

    @staticmethod
    def latitude_invalid(o: _Any) -> bool:
        return not isinstance(o, float) or o < -90 or o > 90

    @staticmethod
    def longitude_invalid(o: _Any) -> bool:
        return not isinstance(o, float) or o < -180 or o > 180

    def bake(self) -> None:
        def unit(row: dict[str, _Any], i: int) -> None:
            self._read_rows += 1
            self._t = row["t"]
            speed = row["speed"]
            if PostProcessor.time_invalid(self._t) or PostProcessor.speed_invalid(speed):
                self._invalid_rows.append(i)
                return
            if self._start_time is None:
                self._start_time = self._t
            if self._min_speed is None or speed < self._min_speed:
                self._min_speed = speed
            if self._max_speed is None or speed > self._max_speed:
                self._max_speed = speed
            self._avg_speed = speed if self._avg_speed is None else (self._avg_speed * self._valid_rows + speed) / (
                    self._valid_rows + 1)
            lat = row["latitude"]
            lon = row["longitude"]
            if not row["gps_valid"] or PostProcessor.latitude_invalid(lat) or PostProcessor.longitude_invalid(lon):
                self._gps_invalid_rows.append(i)
            else:
                if self._min_lat is None or lat < self._min_lat:
                    self._min_lat = lat
                if self._min_lon is None or lon < self._min_lon:
                    self._min_lon = lon
                self._gps_valid_count += 1
            self._valid_rows += 1

        self.foreach(unit, False)
        self._end_time = self._t

    def baking_results(self) -> tuple[str, str, str, str, str, str, str, str, str, str, str]:
        if self._read_rows == 0:
            raise LookupError("Not baked")
        start_time, end_time = int(self._start_time * .001), int(self._end_time * .001)
        return (
            f"Baked {self._valid_rows} / {self._read_rows} ROWS",
            f"Baked Rate: {100 * self._valid_rows / self._read_rows:.2f}%",
            f"Skipped Rows: {self._invalid_rows}",
            f"Start Time: {_datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")}",
            f"End Time: {_datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S")}",
            f"Duration: {(duration := end_time - start_time) // 60} MIN {duration % 60} SEC",
            f"v\u2098\u1D62\u2099: {self._min_speed:.2f} KM / H",
            f"v\u2098\u2090\u2093: {self._max_speed:.2f} KM / H",
            f"v\u2090\u1D65\u1D67: {self._avg_speed:.2f} KM / H",
            f"GPS Hit Rate: {100 * self._gps_valid_count / self._valid_rows:.2f}%",
            f"GPS Skipped Rows: {self._gps_invalid_rows}"
        )

    def erase_unit_cache(self) -> None:
        self._t = None
        self._lap_start = None
        self._lap_start_time = None
        self._lap_end_time = None
        self._x.clear()
        self._y.clear()
        self._d.clear()

    def foreach(self, do: _Callable[[dict[str, _Any], int], None], skip_invalid_rows: bool = True,
                skip_gps_invalid_rows: bool = False) -> None:
        self._dataset.load()
        self.erase_unit_cache()
        i = -1
        for row in self._dataset:
            i += 1
            if skip_invalid_rows and i in self._invalid_rows or skip_gps_invalid_rows and i in self._gps_invalid_rows:
                continue
            do(row, i)

    def draw_lap(self, lap_index: int = 0) -> None:
        def unit(row: dict[str, _Any], i: int) -> None:
            if i < (lap := self._laps[lap_index])[0] or i > lap[1]:
                return
            t = row["t"]
            if self._lap_start_time is None:
                self._lap_start_time = t
            self._lap_end_time = t
            lat = row["latitude"]
            lon = row["longitude"]
            self._d.append(row["speed"])
            self._x.append(dlon2meters(lon - self._min_lon, lat))
            self._y.append(dlat2meters(lat - self._min_lat))

        self.foreach(unit, True, True)
        self._x.append(0)
        self._y.append(0)
        self._d.append(self._max_speed)
        _scatter(self._x, self._y, c=self._d, cmap="hot_r")
        duration = int((self._lap_end_time - self._lap_start_time) * .001)
        _title(f"Lap {lap_index} ({duration // 60} MIN {duration % 60} SEC)")
        _colorbar()
        _show()

    def process(self, vehicle_hit_box: float = 3, min_lap_time: float = 30) -> None:
        path = []

        def unit(row: dict[str, _Any], i: int) -> None:
            if self._lap_start is None:
                self._lap_start = i
            t = row["t"]
            if self._lap_start_time is None:
                self._lap_start_time = t
            lat = row["latitude"]
            lon = row["longitude"]
            p = (round(dlat2meters(lat - self._min_lat) / vehicle_hit_box),
                 round(dlon2meters(lon - self._min_lon, lat) / vehicle_hit_box))
            try:
                index = path.index(p)
            except ValueError:
                index = -1
            if 0 < index < .5 * len(path) and self._lap_start is not None and (
                    t - self._lap_start_time) * .001 >= min_lap_time:
                self._laps.append((self._lap_start, i))
                path.clear()
                self._lap_start = None
            path.append(p)

        self.foreach(unit, True, True)
        if len(self._laps) == 0:
            self._laps.append((0, self._read_rows))

    def num_laps(self) -> int:
        return len(self._laps)
