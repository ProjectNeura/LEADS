from typing import override as _override, Iterator as _Iterator, Any as _Any

from leads import Controller as _Controller, SRWDataContainer as _SRWDataContainer, \
    DRWDataContainer as _DRWDataContainer
from leads.data_persistence import Dataset as _Dataset


class ReplayController(_Controller):
    def __init__(self, dataset: _Dataset) -> None:
        super().__init__()
        self._dataset: _Iterator[dict[str, _Any]] = iter(dataset)


class SRWReplayController(ReplayController):
    @_override
    def read(self) -> _SRWDataContainer:
        return _SRWDataContainer(**next(self._dataset))


class DRWReplayController(ReplayController):
    @_override
    def read(self) -> _DRWDataContainer:
        return _DRWDataContainer(**next(self._dataset))
