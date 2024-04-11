from importlib.util import find_spec as _find_spec

if not _find_spec("pandas"):
    raise ImportError("Please install `pandas` to run this module\n>>>pip install pandas")

from typing import override as _override

from leads import Controller as _Controller, SRWDataContainer as _SRWDataContainer, \
    DRWDataContainer as _DRWDataContainer


class Dataset(object):
    def __init__(self, data_dir: str, instruction_file: str) -> None:
        self._data_dir: str = data_dir
        self._instruction_file: str = instruction_file


class ReplayController(_Controller):
    def __init__(self, dataset: Dataset) -> None:
        super().__init__()
        self._dataset: Dataset = dataset

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)


class SRWReplayController(ReplayController):
    @_override
    def read(self) -> _SRWDataContainer:
        return _SRWDataContainer()


class DRWReplayController(ReplayController):
    @_override
    def read(self) -> _DRWDataContainer:
        return _DRWDataContainer()
