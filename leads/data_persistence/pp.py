from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from datetime import datetime as _datetime
from typing import Any as _Any, Callable as _Callable, override as _override, Generator as _Generator

from matplotlib.pyplot import scatter as _scatter, show as _show, title as _title, colorbar as _colorbar

from leads.data import dlat2meters, dlon2meters
from leads.data_persistence.core import CSVDataset, DEFAULT_HEADER
from ._computational import sqrt as _sqrt


class Inference(object, metaclass=_ABCMeta):
    def __init__(self, required_depth: tuple[int, int] = (0, 0)) -> None:
        self._required_depth: tuple[int, int] = required_depth

    def depth(self) -> tuple[int, int]:
        return self._required_depth

    @_abstractmethod
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        raise NotImplementedError


class SpeedInferenceBase(Inference, metaclass=_ABCMeta):
    @staticmethod
    def skip(row: dict[str, _Any]) -> bool:
        return not PostProcessor.speed_invalid(row["speed"])


class SafeSpeedInference(SpeedInferenceBase):
    """
    Infer the speed based on the front wheel speed or the rear wheel speed.

    v = min(fws, rws)
    """

    def __init__(self) -> None:
        super().__init__((0, 0))

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        row = rows[0]
        if SpeedInferenceBase.skip(row):
            return
        speed = None
        if not PostProcessor.speed_invalid(s := row["front_wheel_speed"]):
            speed = s
        if not PostProcessor.speed_invalid(s := row["rear_wheel_speed"]) and (speed is None or s < speed):
            speed = s
        return None if speed is None else {"speed": speed}


class SpeedInferenceByAcceleration(SpeedInferenceBase):
    """
    Infer the speed based on the acceleration.

    v = ∫a(t)dt
    """

    def __init__(self):
        super().__init__((-1, 0))

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        base, target = rows
        t_0, t, s_0, a_0 = base["t"], target["t"], base["speed"], base["forward_acceleration"]
        if (SpeedInferenceBase.skip(target) or PostProcessor.time_invalid(t_0) or
                PostProcessor.time_invalid(t) or PostProcessor.speed_invalid(s_0) or
                PostProcessor.acceleration_invalid(a_0)):
            return
        a = target["forward_acceleration"]
        if PostProcessor.acceleration_invalid(a):
            a = a_0
        return {"speed": s_0 + .0005 * (a_0 + a) * (t - t_0)}


class SpeedInferenceByMileages(SpeedInferenceBase):
    """
    Infer the speed based on the mileages.

    v = ds/dt
    """

    def __init__(self) -> None:
        super().__init__((-1, 0))

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        base, target = rows
        t_0, t, d_0, d = base["t"], target["t"], base["mileage"], target["mileage"]
        return None if (SpeedInferenceBase.skip(target) or PostProcessor.time_invalid(t_0) or
                        PostProcessor.time_invalid(t) or PostProcessor.mileage_invalid(d_0) or
                        PostProcessor.mileage_invalid(d)) else {
            "speed": 3600000 * abs(d - d_0) / (t - t_0)
        }


class SpeedInferenceByGPSGroundSpeed(SpeedInferenceBase):
    """
    Infer the speed based on the GPS ground speed.
    """

    def __init__(self) -> None:
        super().__init__((0, 0))

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        row = rows[0]
        ground_speed = row["gps_ground_speed"]
        return None if SpeedInferenceBase.skip(row) or PostProcessor.speed_invalid(ground_speed) else {
            "speed": ground_speed
        }


class SpeedInferenceByGPSPositions(SpeedInferenceBase):
    """
    Infer the speed based on the GPS positions.

    v = ds/dt
    """

    def __init__(self) -> None:
        super().__init__((-1, 0))

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        base, target = rows
        t_0, t = base["t"], target["t"]
        lat_0, lat, lon_0, lon = base["latitude"], target["latitude"], base["longitude"], target["longitude"]
        return None if (SpeedInferenceBase.skip(target) or PostProcessor.time_invalid(t_0) or
                        PostProcessor.time_invalid(t) or PostProcessor.latitude_invalid(lat_0) or
                        PostProcessor.latitude_invalid(lat) or PostProcessor.longitude_invalid(lon_0) or
                        PostProcessor.longitude_invalid(lon)) else {
            "speed": 3600 * _sqrt(dlon2meters(lon - lon_0, .5 * (lat_0 + lat)) ** 2 + dlat2meters(lat - lat_0) ** 2) / (
                    t - t_0)
        }


class InferredDataset(CSVDataset):
    _raw_data: list[dict[str, _Any]] = []
    _inferred_data: list[dict[str, _Any]] = []

    @staticmethod
    def merge(raw: dict[str, _Any], inferred: dict[str, _Any]) -> None:
        """
        Merge the inferred data to the raw data. Overwrite if conflicts. It directly alters the raw data object.
        :param raw: the raw data
        :param inferred: the difference data
        """
        for key in inferred.keys():
            raw[key] = inferred[key]

    def complete(self, *inferences: Inference, enhanced: bool = False) -> None:
        """
        Infer the missing values in the dataset.
        :param inferences: inferences to apply
        :param enhanced: True: use inferred data to infer other data; False: use only raw data to infer other data
        """
        if DEFAULT_HEADER in self.read_header():
            raise KeyError("Your dataset must include the default header")
        self.require_loaded()
        for row in super().__iter__():
            self._raw_data.append(row)
        length = len(self._raw_data)
        self._inferred_data = [{} for _ in range(length)]
        for i in range(length):
            for inference in inferences:
                p, f = inference.depth()
                p, f = i + p, i + f + 1
                d = []
                if 0 <= p < length and 0 <= f <= length:
                    for j in range(p, f):
                        row = self._raw_data[j]
                        if enhanced:
                            InferredDataset.merge(row, self._inferred_data[j])
                        d.append(row)
                    if (r := inference.complete(*d)) is not None:
                        InferredDataset.merge(self._inferred_data[i], r)

    def __len__(self) -> int:
        return len(self._raw_data)

    @_override
    def __iter__(self) -> _Generator[dict[str, _Any], None, None]:
        for i in range(len(self._raw_data)):
            InferredDataset.merge(row := self._raw_data[i], self._inferred_data[i])
            yield row

    @_override
    def close(self) -> None:
        super().close()
        self._raw_data.clear()
        self._inferred_data.clear()


class PostProcessor(object):
    def __init__(self, dataset: CSVDataset) -> None:
        if DEFAULT_HEADER in dataset.read_header():
            raise KeyError("Your dataset must include the default header")
        self._dataset: CSVDataset = dataset

        # baking variables
        self._read_rows: int = 0
        self._valid_rows: int = 0
        self._invalid_rows: list[int] = []
        self._start_time: float | None = None
        self._end_time: float | None = None
        self._min_speed: float | None = None
        self._max_speed: float | None = None
        self._start_mileage: float | None = None
        self._end_mileage: float | None = None
        self._gps_valid_count: int = 0
        self._gps_invalid_rows: list[int] = []
        self._min_lat: float | None = None
        self._min_lon: float | None = None

        # process variables
        self._laps: list[tuple[int, int, float]] = []

        # unit variables (not reusable)
        self._t: float | None = None
        self._lap_start: int | None = None
        self._lap_start_time: float | None = None
        self._lap_end_time: float | None = None
        self._lap_start_mileage: float | None = None
        self._lap_end_mileage: float | None = None
        self._x: list[float] = []
        self._y: list[float] = []
        self._d: list[float] = []

    @staticmethod
    def time_invalid(o: _Any) -> bool:
        return not isinstance(o, float) and not isinstance(o, int)

    @staticmethod
    def speed_invalid(o: _Any) -> bool:
        return not isinstance(o, float) or o != o or o < 0

    @staticmethod
    def acceleration_invalid(o: _Any) -> bool:
        return not isinstance(o, float) or o != o

    @staticmethod
    def mileage_invalid(o: _Any) -> bool:
        return not isinstance(o, float) or o != o or o < 0

    @staticmethod
    def latitude_invalid(o: _Any) -> bool:
        return not isinstance(o, float) or o != o or not -90 < o < 90

    @staticmethod
    def longitude_invalid(o: _Any) -> bool:
        return not isinstance(o, float) or o != o or not -180 < o < 180

    def bake(self) -> None:
        def unit(row: dict[str, _Any], i: int) -> None:
            self._read_rows += 1
            self._t = row["t"]
            speed = row["speed"]
            mileage = row["mileage"]
            if PostProcessor.time_invalid(self._t) or PostProcessor.speed_invalid(
                    speed) or PostProcessor.mileage_invalid(mileage):
                self._invalid_rows.append(i)
                return
            if self._start_time is None:
                self._start_time = self._t
            if self._min_speed is None or speed < self._min_speed:
                self._min_speed = speed
            if self._max_speed is None or speed > self._max_speed:
                self._max_speed = speed
            if self._lap_start_mileage is None:
                self._start_mileage = mileage
            self._end_mileage = mileage
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
        if self._valid_rows == 0:
            raise RuntimeError(f"Baked {self._valid_rows} / {self._read_rows} rows")
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
            f"v\u2090\u1D65\u1D67: {3600 * (self._end_mileage - self._start_mileage) / duration:.2f} KM / H",
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

    def draw_lap(self, lap_index: int = -1) -> None:
        if lap_index < 0:
            for i in range(len(self._laps)):
                self.draw_lap(i)

        def unit(row: dict[str, _Any], index: int) -> None:
            if index < (lap := self._laps[lap_index])[0] or index > lap[1]:
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
            mileage = row["mileage"]
            if self._lap_start_mileage is None:
                self._lap_start_mileage = mileage
            self._lap_end_mileage = mileage
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
                self._laps.append((self._lap_start, i, self._lap_end_mileage - self._lap_start_mileage))
                path.clear()
                self._lap_start = None
            path.append(p)

        self.foreach(unit, True, True)
        if len(self._laps) == 0:
            self._laps.append((0, self._read_rows, self._lap_end_mileage))

    def num_laps(self) -> int:
        return len(self._laps)

    def process_results(self) -> tuple[str, str]:
        return (
            f"Number of Laps Detected: {len(self._laps)}",
            f"Call `draw_lap()` for further information."
        )

    def close(self) -> None:
        self._dataset.close()
