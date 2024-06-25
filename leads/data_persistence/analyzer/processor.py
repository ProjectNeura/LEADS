from datetime import datetime as _datetime
from typing import Any as _Any, Callable as _Callable, Sequence as _Sequence

from leads.data import dlat2meters, dlon2meters, format_duration
from leads.data_persistence.core import CSVDataset, DEFAULT_HEADER
from .._computational import sqrt as _sqrt


class Processor(object):
    def __init__(self, dataset: CSVDataset) -> None:
        if DEFAULT_HEADER in dataset.read_header():
            raise KeyError("Your dataset must include the default header")
        self._dataset: CSVDataset = dataset

        # baking variables
        self._read_rows_count: int = 0
        self._valid_rows_count: int = 0
        self._invalid_rows: list[int] = []
        self._start_time: int | None = None
        self._end_time: int | None = None
        self._duration: int | None = None
        self._min_speed: float | None = None
        self._max_speed: float | None = None
        self._avg_speed: float | None = None
        self._start_mileage: float | None = None
        self._end_mileage: float | None = None
        self._distance: float | None = None
        self._gps_valid_count: int = 0
        self._gps_invalid_rows: list[int] = []
        self._min_lat: float | None = None
        self._min_lon: float | None = None

        # process variables
        self._laps: list[tuple[int, int, int, float, float]] = []
        self._max_lap_duration: int | None = None
        self._max_lap_distance: float | None = None
        self._max_lap_avg_speed: float | None = None

        # unit variables (not reusable)
        self._lap_start: int | None = None
        self._lap_start_time: int | None = None
        self._lap_start_mileage: float | None = None
        self._lap_x: list[float] = []
        self._lap_y: list[float] = []
        self._lap_d: list[float] = []
        self._max_lap_x: float | None = None
        self._max_lap_y: float | None = None

    def dataset(self) -> CSVDataset:
        return self._dataset

    @staticmethod
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

    @staticmethod
    def time_invalid(o: _Any) -> bool:
        return not isinstance(o, int)

    @staticmethod
    def speed_invalid(o: _Any) -> bool:
        return not isinstance(o, int | float) or o != o or o < 0

    @staticmethod
    def acceleration_invalid(o: _Any) -> bool:
        return not isinstance(o, int | float) or o != o

    @staticmethod
    def mileage_invalid(o: _Any) -> bool:
        return not isinstance(o, int | float) or o != o

    @staticmethod
    def latitude_invalid(o: _Any) -> bool:
        return not isinstance(o, int | float) or o != o or not -90 < o < 90

    @staticmethod
    def longitude_invalid(o: _Any) -> bool:
        return not isinstance(o, int | float) or o != o or not -180 < o < 180

    def bake(self) -> None:
        """
        Prepare the prerequisites for `process()`.
        """

        def unit(row: dict[str, _Any], i: int) -> None:
            self._read_rows_count += 1
            t = int(row["t"])
            speed = row["speed"]
            mileage = row["mileage"]
            if Processor.time_invalid(t) or Processor.speed_invalid(
                    speed) or Processor.mileage_invalid(mileage):
                self._invalid_rows.append(i)
                return
            if self._start_time is None:
                self._start_time = t
            self._end_time = t
            if self._min_speed is None or speed < self._min_speed:
                self._min_speed = speed
            if self._max_speed is None or speed > self._max_speed:
                self._max_speed = speed
            if self._start_mileage is None:
                self._start_mileage = mileage
            self._end_mileage = mileage
            lat = row["latitude"]
            lon = row["longitude"]
            if not row["gps_valid"] or Processor.latitude_invalid(lat) or Processor.longitude_invalid(lon):
                self._gps_invalid_rows.append(i)
            else:
                if self._min_lat is None or lat < self._min_lat:
                    self._min_lat = lat
                if self._min_lon is None or lon < self._min_lon:
                    self._min_lon = lon
                self._gps_valid_count += 1
            self._valid_rows_count += 1

        self.foreach(unit, False)
        if self._valid_rows_count == 0:
            raise LookupError("Failed to bake")
        self._duration = self._end_time - self._start_time
        self._distance = self._end_mileage - self._start_mileage
        self._avg_speed = 3600000 * self._distance / self._duration

    @staticmethod
    def _hide_others(seq: _Sequence[_Any], limit: int) -> str:
        return f"[{", ".join(map(str, seq[:limit]))}, and {diff} others]" if (diff := len(seq) - limit) > 0 else str(
            seq)

    def baking_results(self) -> tuple[str, str, str, str, str, str, str, str, str, str, str, str]:
        """
        Get the results of the baking process.
        :return: the results in sentences
        """
        if self._read_rows_count == 0:
            raise LookupError("Not baked")
        if self._valid_rows_count == 0:
            raise LookupError(
                f"Failed to baked {self._read_rows_count - self._valid_rows_count} / {self._read_rows_count} rows")
        return (
            f"Baked {self._valid_rows_count} / {self._read_rows_count} ROWS",
            f"Baking Rate: {100 * self._valid_rows_count / self._read_rows_count:.2f}%",
            f"Skipped Rows: {Processor._hide_others(self._invalid_rows, 5)}",
            f"Start Time: {_datetime.fromtimestamp(self._start_time * .001).strftime("%Y-%m-%d %H:%M:%S")}",
            f"End Time: {_datetime.fromtimestamp(self._end_time * .001).strftime("%Y-%m-%d %H:%M:%S")}",
            f"Duration: {format_duration(self._duration * .001)}",
            f"Distance: {self._distance:.2f} KM",
            f"v\u2098\u1D62\u2099: {self._min_speed:.2f} KM / H",
            f"v\u2098\u2090\u2093: {self._max_speed:.2f} KM / H",
            f"v\u2090\u1D65\u1D4D: {self._avg_speed:.2f} KM / H",
            f"GPS Hit Rate: {100 * self._gps_valid_count / self._valid_rows_count:.2f}%",
            f"GPS Skipped Rows: {Processor._hide_others(self._gps_invalid_rows, 5)}"
        )

    def erase_unit_cache(self) -> None:
        self._lap_start = None
        self._lap_start_time = None
        self._lap_start_mileage = None
        self._lap_x.clear()
        self._lap_y.clear()
        self._lap_d.clear()

    def foreach(self, do: _Callable[[dict[str, _Any], int], None], skip_invalid_rows: bool = True,
                skip_gps_invalid_rows: bool = False) -> None:
        self.erase_unit_cache()
        i = -1
        for row in self._dataset:
            i += 1
            if skip_invalid_rows and i in self._invalid_rows or skip_gps_invalid_rows and i in self._gps_invalid_rows:
                continue
            do(row, i)

    def process(self, lap_time_assertions: _Sequence[float] | None = None, vehicle_hit_box: float = 3,
                min_lap_time: float = 30) -> None:
        """
        Split the laps.
        :param lap_time_assertions: the manually timed laps in seconds
        :param vehicle_hit_box: the vehicle hit box in meters
        :param min_lap_time: the minimum lap time in seconds
        :return:
        """
        asserted = lap_time_assertions is not None

        def shared_pre(row: dict[str, _Any], i: int) -> tuple[int, float, float]:
            if self._lap_start is None:
                self._lap_start = i
            t = int(row["t"])
            if self._lap_start_time is None:
                self._lap_start_time = t
            mileage = row["mileage"]
            if self._lap_start_mileage is None:
                self._lap_start_mileage = mileage
            return (dt := t - self._lap_start_time), (
                ds := mileage - self._lap_start_mileage), 3600000 * ds / dt if dt else 0

        def shared_post(duration: float, distance: float, avg_speed: float) -> None:
            if self._max_lap_duration is None or duration > self._max_lap_duration:
                self._max_lap_duration = duration
            if self._max_lap_distance is None or distance > self._max_lap_distance:
                self._max_lap_distance = distance
            if self._max_lap_avg_speed is None or avg_speed > self._max_lap_avg_speed:
                self._max_lap_avg_speed = avg_speed

        def asserted_unit(row: dict[str, _Any], i: int) -> None:
            duration, distance, avg_speed = shared_pre(row, i)
            next_lap_index = len(self._laps)
            if next_lap_index < len(lap_time_assertions) and duration >= lap_time_assertions[next_lap_index] * 1000:
                shared_post(duration, distance, avg_speed)
                self._laps.append((self._lap_start, i, duration, distance, avg_speed))
                self.erase_unit_cache()

        path = []

        def unit(row: dict[str, _Any], i: int) -> None:
            lat = row["latitude"]
            lon = row["longitude"]
            p = (round(dlat2meters(lat - self._min_lat) / vehicle_hit_box),
                 round(dlon2meters(lon - self._min_lon, lat) / vehicle_hit_box))
            try:
                index = path.index(p)
            except ValueError:
                index = -1
            duration, distance, avg_speed = shared_pre(row, i)
            if (0 < index < .5 * len(path) and self._lap_start is not None and duration >= min_lap_time * 1000 and
                    distance * 2000 > vehicle_hit_box):
                shared_post(duration, distance, avg_speed)
                self._laps.append((self._lap_start, i, duration, distance, avg_speed))
                path.clear()
                self.erase_unit_cache()
            else:
                path.append(p)

        self.foreach(asserted_unit if asserted else unit, True, not asserted)

    def suggest_on_lap(self, lap_index: int) -> tuple[str, str]:
        a, b, duration, distance, avg_speed = self._laps[lap_index]
        d = self._avg_speed - avg_speed
        return (
            f"Lap {lap_index + 1} lasts for {format_duration(duration * .001)}",
            f"{abs(d):.2f} KM / H {"slower" if d < 0 else "faster"} than average"
        )

    def num_laps(self) -> int:
        return len(self._laps)

    def results(self) -> tuple[str, str]:
        """
        Get the results of the processor.
        :return: the results in sentences
        """
        return (
            f"Number of Laps Detected: {len(self._laps)}",
            f"Call `draw_lap()` for further information."
        )

    def close(self) -> None:
        self._dataset.close()