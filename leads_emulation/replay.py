from typing import override as _override, Iterator as _Iterator, Any as _Any, TypeVar as _TypeVar, \
    Generic as _Generic

from leads import Controller as _Controller, DataContainer as _DataContainer
from leads.data_persistence import CSVDataset as _CSVDataset

T = _TypeVar("T", bound=_DataContainer)


class ReplayController(_Controller, _Generic[T]):
    def __init__(self, dataset: _CSVDataset, data_container_constructor: type[T]) -> None:
        super().__init__()
        self._dataset: _CSVDataset = dataset
        self._constructor: type[T] = data_container_constructor
        self._iterator: _Iterator[dict[str, _Any]] = iter(dataset)

    @_override
    def read(self) -> T:
        try:
            d = next(self._iterator)
        except StopIteration:
            return self._constructor()
        t = d.pop("t")
        dc = self._constructor(**d)
        dc._time_stamp = t
        return dc

    @_override
    def close(self) -> None:
        self._dataset.close()
