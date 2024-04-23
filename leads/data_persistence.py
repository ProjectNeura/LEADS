from operator import add as _add, sub as _sub, mul as _mul, truediv as _truediv, floordiv as _floordiv, lt as _lt, \
    le as _le, gt as _gt, ge as _ge
from typing import TextIO as _TextIO, TypeVar as _TypeVar, Generic as _Generic, Sequence as _Sequence, \
    override as _override, Self as _Self, Iterator as _Iterator, Callable as _Callable, Iterable as _Iterable, \
    Generator as _Generator, Any as _Any

from numpy import mean as _mean, array as _array
from numpy.linalg import norm as _norm
from pandas import read_csv as _read_csv, DataFrame as _DataFrame
from pandas.io.parsers import TextFileReader as _TextFileReader

from leads.types import Compressor as _Compressor

T = _TypeVar("T")


def mean_compressor(sequence: list[T], target_size: int) -> list[T]:
    """
    A compression method that reduces data memory usage by averaging adjacent numbers and merging them.
    :param sequence: the sequence to compress
    :param target_size: expected size
    :return: the compressed sequence
    """
    chunk_size = int(len(sequence) / target_size)
    if chunk_size < 2:
        return sequence
    r = []
    for i in range(target_size - 1):
        r.append(_mean(sequence[i * chunk_size: (i + 1) * chunk_size]))
    r.append(_mean(sequence[(target_size - 1) * chunk_size:]))
    return r


class DataPersistence(_Sequence[T], _Generic[T]):
    def __init__(self,
                 max_size: int = -1,
                 chunk_scale: int = 1,
                 compressor: _Compressor[T] = mean_compressor) -> None:
        """
        :param max_size: maximum cached size
        :param chunk_scale: chunk scaling factor (compression)
        :param compressor: compressor interface
        """
        self._max_size: int = max_size
        self._chunk_scale: int = chunk_scale
        self._compressor: _Compressor[T] = compressor
        self._data: list[T] = []
        self._chunk: list[T] = []
        self._chunk_size: int = chunk_scale

    @_override
    def __len__(self) -> int:
        return len(self._data)

    @_override
    def __getitem__(self, item: int | slice) -> T | list[T]:
        return self._data[item]

    @_override
    def __str__(self) -> str:
        return str(self._data)

    def to_list(self) -> list[T]:
        return self._data.copy()

    def _push_to_data(self, element: T) -> None:
        self._data.append(element)
        if self._max_size < 2:
            return
        if len(self._data) >= self._max_size:
            self._data = self._compressor(self._data, int(len(self._data) * .5))
            self._chunk_size *= 2

    def append(self, element: T) -> None:
        if self._chunk_size == 1:
            return self._push_to_data(element)
        self._chunk.append(element)
        if len(self._chunk) >= self._chunk_size:
            for e in self._compressor(self._chunk, self._chunk_scale):
                self._push_to_data(e)
            self._chunk.clear()


E = _TypeVar("E")


class Vector(_Sequence[E], _Iterable[E], _Generic[E]):
    def __init__(self, *coordinates: E) -> None:
        self._d: int = len(coordinates)
        self._coordinates: tuple[E, ...] = coordinates

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


class CSVCollection(object):
    def __init__(self, file: str | _TextIO, header: tuple[str, ...], *columns: DataPersistence | None) -> None:
        self._file: _TextIO = open(file, "w") if isinstance(file, str) else file
        self._d: int = len(header)
        self._header: tuple[str, ...] = header
        if len(columns) != self._d:
            raise ValueError("Unmatched columns and header")
        self._columns: tuple[DataPersistence | None, ...] = columns
        self._i: int = 0
        self.write_header()

    def header(self) -> tuple[str, ...]:
        return self._header

    def write_header(self) -> None:
        self._file.write(f"{",".join(self._header)}\n")

    def write_frame(self, *data: _Any) -> None:
        if len(data) != self._d:
            raise ValueError("Unmatched data and header")
        frame = {}
        for i in range(self._d):
            frame[self._header[i]] = d = data[i]
            if column := self._columns[i]:
                column.append(d)
        _DataFrame(data=frame, index=[self._i]).to_csv(self._file, mode="a", header=False)
        self._i += 1

    def close(self) -> None:
        self._file.close()


class Dataset(_Iterable[dict[str, _Any]]):
    def __init__(self, file: str, chunk_size: int = 100) -> None:
        self._file: str = file
        self._chunk_size: int = chunk_size
        self._csv: _TextFileReader | None = None

    @_override
    def __iter__(self) -> _Generator[dict[str, _Any], None, None]:
        if self._csv is None:
            raise EOFError("Dataset not loaded")
        while True:
            try:
                chunk = next(self._csv)
            except StopIteration:
                break
            for i in range(len(chunk)):
                yield chunk.iloc[i].to_dict()

    def load(self) -> None:
        self._csv = _read_csv(self._file, chunksize=self._chunk_size, low_memory=False)
