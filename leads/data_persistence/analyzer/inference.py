from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from typing import Any as _Any, override as _override, Generator as _Generator, Literal as _Literal

from leads.data_persistence.analyzer.utils import time_invalid, speed_invalid, acceleration_invalid, \
    mileage_invalid, latitude_invalid, longitude_invalid, distance_between
from leads.data_persistence.core import CSVDataset, DEFAULT_HEADER, VISUAL_HEADER_ONLY


class Inference(object, metaclass=_ABCMeta):
    def __init__(self, required_depth: tuple[int, int] = (0, 0),
                 required_header: tuple[str, ...] = DEFAULT_HEADER) -> None:
        """
        Declare the scale of data this inference requires.
        :param required_depth: (-depth backward, depth forward)
        :param required_header: the necessary header that the dataset must contain for this inference to work
        """
        self._required_depth: tuple[int, int] = required_depth
        self._required_header: tuple[str, ...] = required_header

    def depth(self) -> tuple[int, int]:
        """
        :return: (-depth backward, depth forward)
        """
        return self._required_depth

    def header(self) -> tuple[str, ...]:
        return self._required_header

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
        return not speed_invalid(row["speed"])


class SafeSpeedInference(SpeedInferenceBase):
    """
    Infer the speed based on the front wheel speed or the rear wheel speed.

    v = min(fws, rws)
    """

    def __init__(self) -> None:
        super().__init__()

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        row = rows[0]
        if SpeedInferenceBase.skip(row):
            return
        speed = None
        if not speed_invalid(s := row["front_wheel_speed"]):
            speed = s
        if not speed_invalid(s := row["rear_wheel_speed"]) and (speed is None or s < speed):
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
        if (SpeedInferenceBase.skip(target) or time_invalid(t_0) or
                time_invalid(t) or speed_invalid(v_0) or
                acceleration_invalid(a_0)):
            return
        a = target["forward_acceleration"]
        if acceleration_invalid(a):
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
        return None if (SpeedInferenceBase.skip(target) or time_invalid(t_0) or
                        time_invalid(t) or mileage_invalid(s_0) or
                        mileage_invalid(s)) else {
            "speed": abs(3600000 * (s - s_0) / (t - t_0))
        }


class SpeedInferenceByGPSGroundSpeed(SpeedInferenceBase):
    """
    Infer the speed based on the GPS ground speed.
    """

    def __init__(self) -> None:
        super().__init__()

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        row = rows[0]
        ground_speed = row["gps_ground_speed"]
        return None if (SpeedInferenceBase.skip(row) or not row["gps_valid"] or
                        speed_invalid(ground_speed)) else {
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
        return None if (SpeedInferenceBase.skip(target) or time_invalid(t_0) or
                        time_invalid(t) or not base["gps_valid"] or not target["gps_valid"] or
                        latitude_invalid(lat_0) or latitude_invalid(lat) or
                        longitude_invalid(lon_0) or longitude_invalid(lon)) else {
            "speed": abs(3600 * distance_between(lat_0, lon_0, lat, lon) / (t - t_0))
        }


class ForwardAccelerationInferenceBase(Inference, metaclass=_ABCMeta):
    @staticmethod
    def skip(row: dict[str, _Any]) -> bool:
        return not mileage_invalid(row["forward_acceleration"])


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
        return None if (ForwardAccelerationInferenceBase.skip(target) or time_invalid(t_0) or
                        time_invalid(t) or speed_invalid(v_0) or
                        speed_invalid(v)) else {
            "forward_acceleration": (v - v_0) / (t - t_0)
        }


class MileageInferenceBase(Inference, metaclass=_ABCMeta):
    @staticmethod
    def skip(row: dict[str, _Any]) -> bool:
        return not mileage_invalid(row["mileage"])


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
        if (MileageInferenceBase.skip(target) or time_invalid(t_0) or time_invalid(t) or
                speed_invalid(v_0) or mileage_invalid(s_0)):
            return
        v = target["speed"]
        if speed_invalid(v):
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
        return None if (MileageInferenceBase.skip(target) or mileage_invalid(s_0) or
                        not base["gps_valid"] or not target["gps_valid"] or latitude_invalid(lat_0) or
                        latitude_invalid(lat) or longitude_invalid(lon_0) or
                        longitude_invalid(lon)) else {
            "mileage": s_0 + .001 * distance_between(lat_0, lon_0, lat, lon)
        }


class VisualDataRealignmentByLatency(Inference):
    def __init__(self, *channels: _Literal["front", "left", "right", "rear"]) -> None:
        super().__init__((0, 1), VISUAL_HEADER_ONLY)
        self._channels: tuple[_Literal["front", "left", "right", "rear"], ...] = channels if channels else (
            "front", "left", "right", "rear")

    @_override
    def complete(self, *rows: dict[str, _Any], backward: bool = False) -> dict[str, _Any] | None:
        if backward:
            return None
        target, base = rows
        original_target = target.copy()
        t_0, t = target["t"], base["t"]
        for channel in self._channels:
            if (new_latency := t_0 - t + base[f"{channel}_view_latency"]) > 0:
                continue
            target[f"{channel}_view_base64"] = base[f"{channel}_view_base64"]
            target[f"{channel}_view_latency"] = new_latency
        return None if target == original_target else target


class InferredDataset(CSVDataset):
    def __init__(self, file: str, chunk_size: int = 100) -> None:
        super().__init__(file, chunk_size)
        self._raw_data: tuple[dict[str, _Any], ...] = ()
        self._inferred_data: list[dict[str, _Any]] = []

    @_override
    def __len__(self) -> int:
        return len(self._raw_data)

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
        if speed_invalid(row["speed"]):
            injection["speed"] = 0
        if acceleration_invalid(row["forward_acceleration"]):
            injection["forward_acceleration"] = 0
        if mileage_invalid(row["mileage"]):
            injection["mileage"] = 0
        InferredDataset.merge(row, injection)

    def complete(self, *inferences: Inference, enhanced: bool = False, assume_initial_zeros: bool = False) -> None:
        """
        Infer the missing values in the dataset.
        :param inferences: the inferences to apply
        :param enhanced: True: use inferred data to infer other data; False: use only raw data to infer other data
        :param assume_initial_zeros: True: reasonably set any missing data in the first row to zero; False: no change
        """
        for inference in inferences:
            if not set(rh := inference.header()).issubset(ah := self.read_header()):
                raise KeyError(f"Inference {inference} requires header {rh} but the dataset only contains {ah}")
        if assume_initial_zeros:
            self.assume_initial_zeros()
        self._complete(inferences, enhanced, False)
        self._complete(inferences, enhanced, True)

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
