from operator import add as _add, sub as _sub, mul as _mul, truediv as _truediv, floordiv as _floordiv, lt as _lt, \
    le as _le, gt as _gt, ge as _ge
from typing import TextIO as _TextIO, TypeVar as _TypeVar, Generic as _Generic, Sequence as _Sequence, \
    override as _override, Self as _Self, Iterator as _Iterator, Callable as _Callable, Iterable as _Iterable, \
    Generator as _Generator, Any as _Any, SupportsFloat as _SupportsFloat

from numpy import nan as _nan

from leads.types import Compressor as _Compressor, VisualHeader as _VisualHeader, \
    VisualHeaderFull as _VisualHeaderFull, DefaultHeaderFull as _DefaultHeaderFull, DefaultHeader as _DefaultHeader
from ._computational import array as _array, norm as _norm, read_csv as _read_csv, DataFrame as _DataFrame, \
    TextFileReader as _TextFileReader, diff as _diff, ndarray as _ndarray

T = _TypeVar("T", bound=_SupportsFloat)


def weighed_sum(elements: tuple[T, ...], indexes: tuple[float, ...], a: int = 0, b: int | None = None) -> T:
    e = _array(elements[a: b if b else -1])
    w = _diff(_array(indexes[a: b + 1] if b else indexes[a:] + (1,)))
    if len(e.shape) > 1:
        w = w.reshape((-1, 1))
    return Vector(*tuple(s)) if isinstance(s := (e * w).sum(0, keepdims=True)[0], _ndarray) else float(s)


def weighed_mean(elements: tuple[T, ...], indexes: tuple[float, ...], a: int = 0, b: int | None = None) -> T:
    return weighed_sum(elements, indexes, a, b) / (indexes[b] - indexes[a]) if b else weighed_sum(
        elements, indexes, a, b) / (indexes[-1] - indexes[a] + 1)


def mean_compressor(sequence: dict[T, float], target_size: int) -> dict[T, float]:
    """
    A compression method that reduces data memory usage by averaging adjacent numbers and merging them.
    :param sequence: the sequence to compress
    :param target_size: the expected size
    :return: the compressed sequence
    """
    elements, indexes = tuple(sequence.keys()), tuple(sequence.values())
    chunk_size = int(len(sequence) / target_size)
    if chunk_size < 2:
        return sequence
    r = {weighed_mean(elements, indexes, i * chunk_size, (i + 1) * chunk_size): indexes[i * chunk_size] for i in range(
        target_size - 1)}
    r[weighed_mean(elements, indexes, (target_size - 1) * chunk_size)] = indexes[(target_size - 1) * chunk_size]
    return r


class DataPersistence(_Sequence[T], _Generic[T]):
    def __init__(self, max_size: int = -1, crop_ratio: int = 2, compressor: _Compressor[T] = mean_compressor) -> None:
        """
        :param max_size: the maximum cached size
        :param crop_ratio: new size = max size / crop ratio
        :param compressor: the compressor interface
        """
        if max_size % crop_ratio != 0:
            raise ValueError("Max size must be divisible by crop ratio")
        self._max_size: int = max_size
        self._crop_ratio: int = crop_ratio
        self._new_size: int = max_size // crop_ratio
        self._compressor: _Compressor[T] = compressor
        self._chunk: dict[T, float] = {}
        self._size: int = 0

    @_override
    def __len__(self) -> int:
        return self._size

    @_override
    def __getitem__(self, index: int) -> T | list[T]:
        if index < 0:
            index += len(self)
        if self._max_size < 2:
            return index
        last = None
        for e, i in self._chunk.items():
            if i == index:
                return i
            if i > index:
                return last
            last = e

    @_override
    def __str__(self) -> str:
        return str(self.to_list())

    def sum(self) -> T:
        return weighed_sum(tuple(self._chunk.keys()), tuple(self._chunk.values()))

    def indexes(self) -> list[float]:
        return list(self._chunk.values())

    def weights(self) -> list[float]:
        return list(_diff(self._chunk.values())) + [1]

    def to_list(self) -> list[T]:
        return list(self._chunk.keys())

    def append(self, element: T) -> None:
        if 1 < self._max_size < len(self._chunk) + 1:
            self._chunk = self._compressor(self._chunk, self._new_size)
        self._chunk[element] = self._size
        self._size += 1


E = _TypeVar("E")


class Vector(_Sequence[E], _Iterable[E], _Generic[E]):
    def __init__(self, *coordinates: E) -> None:
        self._d: int = len(coordinates)
        self._coordinates: tuple[E, ...] = coordinates

    @_override
    def __hash__(self) -> int:
        return hash(self._coordinates)

    @_override
    def __len__(self) -> int:
        return self._d

    @_override
    def __iter__(self) -> _Iterator[E]:
        return iter(self._coordinates)

    @_override
    def __getitem__(self, item: int | slice) -> _Self:
        return Vector(*self._coordinates[item])

    @_override
    def __str__(self) -> str:
        return ";".join(map(str, self._coordinates))

    @_override
    def __eq__(self, other: _Self) -> bool:
        return self._coordinates == other._coordinates

    def _check_dimension(self, other: _Self) -> None:
        if other._d != self._d:
            raise ValueError("Cannot perform this operation on two vectors of different dimensions")

    def __neg__(self) -> _Self:
        return Vector(*(-i for i in self._coordinates))

    def __abs__(self) -> _Self:
        return Vector(*(abs(i) for i in self._coordinates))

    def _operate(self, other: _Self | E, operator: _Callable[[E, E], E]) -> _Self:
        if isinstance(other, Vector):
            self._check_dimension(other)
            return Vector(*(operator(self._coordinates[i], other._coordinates[i]) for i in range(self._d)))
        return Vector(*(operator(i, other) for i in self._coordinates))

    def __add__(self, other: _Self | E) -> _Self:
        return self._operate(other, _add)

    def __sub__(self, other: _Self | E) -> _Self:
        return self._operate(other, _sub)

    def __mul__(self, other: _Self | E) -> _Self:
        return self._operate(other, _mul)

    def __truediv__(self, other: _Self | E) -> _Self:
        return self._operate(other, _truediv)

    def __floordiv__(self, other: _Self | E) -> _Self:
        return self._operate(other, _floordiv)

    def distance(self, other: _Self) -> float:
        return float(_norm(_array(self._coordinates) - _array(other._coordinates)))

    def magnitude(self) -> float:
        return self.distance(Vector(*(0,) * self._d))

    def _compare(self, other: _Self | E, comparer: _Callable[[E, E], bool]) -> bool:
        return comparer(self.magnitude(), other.magnitude() if isinstance(other, Vector) else other)

    def __lt__(self, other: _Self | E) -> bool:
        return self._compare(other, _lt)

    def __le__(self, other: _Self | E) -> bool:
        return self._compare(other, _le)

    def __gt__(self, other: _Self | E) -> bool:
        return self._compare(other, _gt)

    def __ge__(self, other: _Self | E) -> bool:
        return self._compare(other, _ge)


class CSV(object):
    def __init__(self, file: str | _TextIO, header: tuple[str, ...], *columns: DataPersistence | None) -> None:
        self._file: _TextIO = open(file, "w") if isinstance(file, str) else file
        self._d: int = len(header)
        self._header: tuple[str, ...] = header
        if (d := self._d - len(columns)) >= 0:
            columns += (None,) * d
        else:
            raise ValueError("Unmatched columns and header")
        self._columns: tuple[DataPersistence | None, ...] = columns
        self._i: int = 0
        self.write_header()

    def header(self) -> tuple[str, ...]:
        return self._header

    def write_header(self) -> None:
        header = f"{",".join(self._header)}\n"
        if not header.startswith("index"):
            header = f"index,{header}"
        self._file.write(header)

    def write_frame(self, *data: _Any) -> None:
        if len(data) != self._d:
            raise ValueError("Unmatched data and header")
        frame = {}
        for i in range(self._d):
            frame[self._header[i]] = d = data[i]
            if column := self._columns[i]:
                column.append(d)
        _DataFrame(frame, [self._i]).to_csv(self._file, mode="a", header=False)
        self._i += 1

    def close(self) -> None:
        self._file.close()


class CSVDataset(_Iterable[dict[str, _Any]]):
    def __init__(self, file: str, chunk_size: int = 100) -> None:
        self._file: str = file
        self._chunk_size: int = chunk_size
        self._csv: _TextFileReader | None = None
        self._header: tuple[str, ...] | None = None
        self._contains_index: bool = False

    def require_loaded(self) -> None:
        if not self._csv or not self._header:
            self.load()

    def read_header(self) -> tuple[str, ...]:
        self.require_loaded()
        return self._header

    @_override
    def __iter__(self) -> _Generator[dict[str, _Any], None, None]:
        self.require_loaded()
        while True:
            try:
                chunk = next(self._csv)
            except StopIteration:
                break
            for i in range(len(chunk)):
                r = chunk.iloc[i].replace(_nan, None).to_dict()
                if self._contains_index:
                    r.pop("index")
                yield r
        self._csv.close()
        self._csv = None

    def __len__(self) -> int:
        self.require_loaded()
        return self._csv.shape[0]

    def load(self) -> None:
        if self._csv:
            return
        header_csv = _read_csv(self._file, chunksize=1)
        self._header = tuple(header_csv.get_chunk().columns)
        if self._header[0] == "index":
            self._header = self._header[1:]
            self._contains_index = True
        header_csv.close()
        self._csv = _read_csv(self._file, chunksize=self._chunk_size, low_memory=False)

    def save(self, file: str | _TextIO) -> None:
        self.require_loaded()
        csv = CSV(file, self._header)
        for row in self:
            csv.write_frame(*row.values())
        csv.close()

    def close(self) -> None:
        if self._csv:
            self._csv.close()


DEFAULT_HEADER: _DefaultHeader = (
    "t", "voltage", "speed", "front_wheel_speed", "rear_wheel_speed", "yaw", "pitch", "roll", "forward_acceleration",
    "lateral_acceleration", "vertical_acceleration", "front_proximity", "left_proximity", "right_proximity",
    "rear_proximity", "mileage", "gps_valid", "gps_ground_speed", "latitude", "longitude"
)
DEFAULT_HEADER_FULL: _DefaultHeaderFull = DEFAULT_HEADER + (
    "steering_position", "throttle", "brake"
)
VISUAL_HEADER_ONLY: tuple[str, str, str, str, str, str, str, str] = (
    "front_view_base64", "front_view_latency", "left_view_base64", "left_view_latency", "right_view_base64",
    "right_view_latency", "rear_view_base64", "rear_view_latency"
)
VISUAL_HEADER: _VisualHeader = DEFAULT_HEADER + VISUAL_HEADER_ONLY
VISUAL_HEADER_FULL: _VisualHeaderFull = DEFAULT_HEADER_FULL + VISUAL_HEADER_ONLY
