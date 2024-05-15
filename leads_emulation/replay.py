from typing import override as _override, Iterator as _Iterator, Any as _Any

from leads import Controller as _Controller, DataContainer as _DataContainer
from leads.data_persistence import CSVDataset as _CSVDataset


class ReplayController(_Controller):
    def __init__(self, dataset: _CSVDataset) -> None:
        super().__init__()
        self._dataset: _CSVDataset = dataset
        self._iterator: _Iterator[dict[str, _Any]] = iter(dataset)

    @_override
    def read(self) -> _DataContainer:
        try:
            d = next(self._iterator)
        except StopIteration:
            return _DataContainer()
        t = d.pop("t")
        dc = _DataContainer(**d)
        dc._time_stamp = t
        return dc

    @_override
    def close(self) -> None:
        self._dataset.close()
