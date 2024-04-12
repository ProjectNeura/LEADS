from typing import override as _override, Iterator as _Iterator, Any as _Any

from leads import Controller as _Controller, SRWDataContainer as _SRWDataContainer, \
    DRWDataContainer as _DRWDataContainer
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


class SRWReplayController(ReplayController):
    @_override
    def read(self) -> _SRWDataContainer:
        d = next(self._iterator)
        t = d.pop("time_stamp")
        dc = _SRWDataContainer(**d)
        dc._time_stamp = t
        return dc


class DRWReplayController(ReplayController):
    @_override
    def read(self) -> _DRWDataContainer:
        d = next(self._iterator)
        t, speed = d.pop("time_stamp")
        dc = _DRWDataContainer(**d)
        dc._time_stamp = t
        return dc
