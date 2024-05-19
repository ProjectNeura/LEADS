from importlib.util import find_spec as _find_spec

if not _find_spec("matplotlib"):
    raise ImportError("Please install `matplotlib` to run this module\n>>>pip install matplotlib")

from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from datetime import datetime as _datetime
from typing import Any as _Any, Callable as _Callable, override as _override, Generator as _Generator, \
    Sequence as _Sequence

from matplotlib.pyplot import figure as _figure, scatter as _scatter, show as _show, title as _title, \
    colorbar as _colorbar, bar as _bar, xticks as _xticks, legend as _legend, xlabel as _xlabel, ylabel as _ylabel

from leads.data import dlat2meters, dlon2meters, format_duration
from leads.data_persistence.core import CSVDataset, DEFAULT_HEADER
from ._computational import sqrt as _sqrt


class Inference(object, metaclass=_ABCMeta):
    def __init__(self, required_depth: tuple[int, int] = (0, 0)) -> None:
        """
        Declare the scale of data this inference requires.
        :param required_depth: (-depth backward, depth forward)
        """
        self._required_depth: tuple[int, int] = required_depth

    def depth(self) -> tuple[int, int]:
        """
        :return: (-depth backward, depth forward)
        """
        return self._required_depth

    @_abstractmethod
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        """
        Infer, based on the data flow, to complete the missing columns.
        :param rows: the data flow with the length of depth backward + depth forward
        :param backward: True: globally reversed; False: regular
        :return:
        """
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

    def __init__(self) -> None:
        super().__init__((-1, 0))

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        base, target = rows
        t_0, t, v_0, a_0 = base["t"], target["t"], base["speed"], base["forward_acceleration"]
        if (SpeedInferenceBase.skip(target) or PostProcessor.time_invalid(t_0) or
                PostProcessor.time_invalid(t) or PostProcessor.speed_invalid(v_0) or
                PostProcessor.acceleration_invalid(a_0)):
            return
        a = target["forward_acceleration"]
        if PostProcessor.acceleration_invalid(a):
            a = a_0
        return {"speed": abs(v_0 + .0018 * (a_0 + a) * (t - t_0))}


class SpeedInferenceByMileage(SpeedInferenceBase):
    """
    Infer the speed based on the mileage.

    v = ds/dt
    """

    def __init__(self) -> None:
        super().__init__((-1, 0))

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        base, target = rows
        t_0, t, s_0, s = base["t"], target["t"], base["mileage"], target["mileage"]
        return None if (SpeedInferenceBase.skip(target) or PostProcessor.time_invalid(t_0) or
                        PostProcessor.time_invalid(t) or PostProcessor.mileage_invalid(s_0) or
                        PostProcessor.mileage_invalid(s)) else {
            "speed": abs(3600000 * (s - s_0) / (t - t_0))
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
        return None if (SpeedInferenceBase.skip(row) or not row["gps_valid"] or
                        PostProcessor.speed_invalid(ground_speed)) else {
            "speed": ground_speed
        }


class SpeedInferenceByGPSPosition(SpeedInferenceBase):
    """
    Infer the speed based on the GPS position.

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
                        PostProcessor.time_invalid(t) or not base["gps_valid"] or not target["gps_valid"] or
                        PostProcessor.latitude_invalid(lat_0) or PostProcessor.latitude_invalid(lat) or
                        PostProcessor.longitude_invalid(lon_0) or PostProcessor.longitude_invalid(lon)) else {
            "speed": abs(3600 * PostProcessor.distance_between(lat_0, lon_0, lat, lon) / (t - t_0))
        }


class ForwardAccelerationInferenceBase(Inference, metaclass=_ABCMeta):
    @staticmethod
    def skip(row: dict[str, _Any]) -> bool:
        return not PostProcessor.mileage_invalid(row["forward_acceleration"])


class ForwardAccelerationInferenceBySpeed(ForwardAccelerationInferenceBase):
    """
    Infer the forward acceleration based on the speed.

    a = dv/dt
    """

    def __init__(self) -> None:
        super().__init__((0, 1))

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        target, base = rows
        t_0, t, v_0, v = target["t"], base["t"], target["speed"], base["speed"]
        return None if (ForwardAccelerationInferenceBase.skip(target) or PostProcessor.time_invalid(t_0) or
                        PostProcessor.time_invalid(t) or PostProcessor.speed_invalid(v_0) or
                        PostProcessor.speed_invalid(v)) else {
            "forward_acceleration": (v - v_0) / (t - t_0)
        }


class MileageInferenceBase(Inference, metaclass=_ABCMeta):
    @staticmethod
    def skip(row: dict[str, _Any]) -> bool:
        return not PostProcessor.mileage_invalid(row["mileage"])


class MileageInferenceBySpeed(MileageInferenceBase):
    """
    Infer the mileage based on the speed.

    s = ∫v(t)dt
    """

    def __init__(self) -> None:
        super().__init__((-1, 0))

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        base, target = rows
        t_0, t, v_0, s_0 = base["t"], target["t"], base["speed"], base["mileage"]
        if (MileageInferenceBase.skip(target) or PostProcessor.time_invalid(t_0) or PostProcessor.time_invalid(t) or
                PostProcessor.speed_invalid(v_0) or PostProcessor.mileage_invalid(s_0)):
            return
        v = target["speed"]
        if PostProcessor.speed_invalid(v):
            v = v_0
        return {"mileage": s_0 + .00000125 * (v_0 + v) * (t - t_0) / 9}


class MileageInferenceByGPSPosition(MileageInferenceBase):
    """
    Infer the mileage based on the speed.

    s = s_0 + Δs
    """

    def __init__(self) -> None:
        super().__init__((-1, 0))

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        base, target = rows
        s_0 = base["mileage"]
        lat_0, lat, lon_0, lon = base["latitude"], target["latitude"], base["longitude"], target["longitude"]
        return None if (MileageInferenceBase.skip(target) or PostProcessor.mileage_invalid(s_0) or
                        not base["gps_valid"] or not target["gps_valid"] or PostProcessor.latitude_invalid(lat_0) or
                        PostProcessor.latitude_invalid(lat) or PostProcessor.longitude_invalid(lon_0) or
                        PostProcessor.longitude_invalid(lon)) else {
            "mileage": s_0 + .001 * PostProcessor.distance_between(lat_0, lon_0, lat, lon)
        }


class InferredDataset(CSVDataset):
    _raw_data: tuple[dict[str, _Any], ...] = ()
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

    def _complete(self, inferences: tuple[Inference, ...], enhanced: bool, backward: bool) -> None:
        num_rows = len(self._raw_data)
        for i in range(num_rows - 1, -1, -1) if backward else range(num_rows):
            for inference in inferences:
                p, f = inference.depth()
                p, f = (i - p, i - f - 1) if backward else (i + p, i + f + 1)
                d = []
                if (-1 < p < num_rows and -1 <= f < num_rows - 1) if backward else (
                        0 <= p < num_rows and 0 < f <= num_rows):
                    for j in range(p, f, -1 if backward else 1):
                        row = self._raw_data[j]
                        if enhanced:
                            InferredDataset.merge(row, self._inferred_data[j])
                        d.append(row)
                    if (r := inference.complete(*d, backward=backward)) is not None:
                        InferredDataset.merge(self._inferred_data[i], r)

    @_override
    def load(self) -> None:
        if self._raw_data:
            return
        super().load()
        raw_data = []
        for row in super().__iter__():
            raw_data.append(row)
        self._raw_data = tuple(raw_data)
        self._inferred_data = [{} for _ in range(len(raw_data))]

    def assume_initial_zeros(self) -> None:
        row = self._raw_data[0]
        injection = {}
        if PostProcessor.speed_invalid(row["speed"]):
            injection["speed"] = 0
        if PostProcessor.acceleration_invalid(row["forward_acceleration"]):
            injection["forward_acceleration"] = 0
        if PostProcessor.mileage_invalid(row["mileage"]):
            injection["mileage"] = 0
        InferredDataset.merge(row, injection)

    def complete(self, *inferences: Inference, enhanced: bool = False, assume_initial_zeros: bool = False) -> None:
        """
        Infer the missing values in the dataset.
        :param inferences: the inferences to apply
        :param enhanced: True: use inferred data to infer other data; False: use only raw data to infer other data
        :param assume_initial_zeros: True: reasonably set any missing data in the first row to zero; False: no change
        """
        if DEFAULT_HEADER in self.read_header():
            raise KeyError("Your dataset must include the default header")
        if assume_initial_zeros:
            self.assume_initial_zeros()
        self._complete(inferences, enhanced, False)
        self._complete(inferences, enhanced, True)

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
        self._raw_data = ()
        self._inferred_data.clear()


class PostProcessor(object):
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
            if PostProcessor.time_invalid(t) or PostProcessor.speed_invalid(
                    speed) or PostProcessor.mileage_invalid(mileage):
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
            if not row["gps_valid"] or PostProcessor.latitude_invalid(lat) or PostProcessor.longitude_invalid(lon):
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
            f"Baked Rate: {100 * self._valid_rows_count / self._read_rows_count:.2f}%",
            f"Skipped Rows: {PostProcessor._hide_others(self._invalid_rows, 5)}",
            f"Start Time: {_datetime.fromtimestamp(self._start_time * .001).strftime("%Y-%m-%d %H:%M:%S")}",
            f"End Time: {_datetime.fromtimestamp(self._end_time * .001).strftime("%Y-%m-%d %H:%M:%S")}",
            f"Duration: {format_duration(self._duration * .001)}",
            f"Distance: {self._distance:.2f} KM",
            f"v\u2098\u1D62\u2099: {self._min_speed:.2f} KM / H",
            f"v\u2098\u2090\u2093: {self._max_speed:.2f} KM / H",
            f"v\u2090\u1D65\u1D67: {self._avg_speed:.2f} KM / H",
            f"GPS Hit Rate: {100 * self._gps_valid_count / self._valid_rows_count:.2f}%",
            f"GPS Skipped Rows: {PostProcessor._hide_others(self._gps_invalid_rows, 5)}"
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

    def draw_lap(self, lap_index: int = -1) -> None:
        if lap_index < 0:
            for i in range(len(self._laps)):
                self.draw_lap(i)
        if lap_index >= len(self._laps):
            raise IndexError("Lap index out of range")

        def unit(row: dict[str, _Any], index: int) -> None:
            if index < (lap := self._laps[lap_index])[0] or index > lap[1]:
                return
            t = int(row["t"])
            if self._lap_start_time is None:
                self._lap_start_time = t
            self._lap_end_time = t
            lat = row["latitude"]
            lon = row["longitude"]
            self._lap_d.append(row["speed"])
            self._lap_x.append(x := dlon2meters(lon - self._min_lon, lat))
            self._lap_y.append(y := dlat2meters(lat - self._min_lat))
            if self._max_lap_x is None or x > self._max_lap_x:
                self._max_lap_x = x
            if self._max_lap_y is None or y > self._max_lap_y:
                self._max_lap_y = y

        self.foreach(unit, True, True)
        far = max(self._max_lap_x, self._max_lap_y)
        self._lap_x.append(far)
        self._lap_y.append(far)
        self._lap_d.append(self._max_speed)
        _figure(figsize=(6, 5))
        _title(f"Lap {lap_index + 1} ({self._laps[lap_index][3]:.2f} KM @ {format_duration(
            self._laps[lap_index][2] * .001)})")
        _scatter(self._lap_x, self._lap_y, c=self._lap_d, cmap="hot_r")
        _xlabel("X (M)")
        _ylabel("Y (M)")
        cb = _colorbar()
        cb.set_label("Speed (KM / H)")
        cb.ax.hlines(self._laps[lap_index][4], 0, 1)
        _show()

    def draw_comparison_of_laps(self, width: float = .3) -> None:
        durations = []
        x0 = []
        distances = []
        x1 = []
        avg_speeds = []
        x2 = []
        x_ticks = []
        i = 1
        for lap in self._laps:
            durations.append(lap[2] / self._max_lap_duration)
            x0.append(i)
            distances.append(lap[3] / self._max_lap_distance)
            x1.append(i + width)
            avg_speeds.append(lap[4] / self._max_lap_avg_speed)
            x2.append(i + 2 * width)
            x_ticks.append(f"L{i}")
            i += 1
        _figure(figsize=(5 * _sqrt(len(self._laps)), 5))
        _bar(x0, durations, width, label="Duration")
        _bar(x1, distances, width, label="Distance")
        _bar(x2, avg_speeds, width, label="Average Speed")
        _xticks(x1, x_ticks)
        _legend()
        _xlabel("Lap")
        _ylabel("Proportion (% / max)")
        _show()

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
