from typing import override as _override, Iterator as _Iterator, Any as _Any

from leads import Controller as _Controller, DataContainer as _DataContainer
from leads.data_persistence import Dataset as _Dataset


class ReplayController(_Controller):
    def __init__(self, dataset: _Dataset) -> None:
        super().__init__()
        self._dataset: _Dataset = dataset
        self._iterator: _Iterator[dict[str, _Any]] = iter(dataset)

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self._dataset.load()

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
