from base64 import b64decode as _b64decode
from io import BytesIO as _BytesIO
from typing import override as _override, Iterator as _Iterator, Any as _Any, TypeVar as _TypeVar, \
    Generic as _Generic, Literal as _Literal

from PIL.Image import open as _open, Image as _Image
from numpy import ndarray as _ndarray, array as _array

from leads import Controller as _Controller, DataContainer as _DataContainer, get_controller as _get_controller, \
    VisualDataContainer as _VisualDataContainer, Device as _Device
from leads.data_persistence import CSVDataset as _CSVDataset
from leads_video import Camera as _Camera

T = _TypeVar("T", bound=_DataContainer)


class ReplayController(_Controller, _Generic[T]):
    def __init__(self, dataset: _CSVDataset, data_container_constructor: type[T]) -> None:
        super().__init__()
        self._dataset: _CSVDataset = dataset
        self._constructor: type[T] = data_container_constructor
        self._iterator: _Iterator[dict[str, _Any]] = iter(dataset)
        self._current_data_container: T | None = None

    @_override
    def read(self) -> T:
        try:
            d = next(self._iterator)
        except StopIteration:
            return self._constructor()
        t = d.pop("t")
        dc = self._constructor(**d)
        setattr(dc, "_time_stamp", t)
        self._current_data_container = dc
        return dc

    def current_data_container(self) -> T | None:
        return self._current_data_container

    @_override
    def close(self) -> None:
        self._dataset.close()


class ReplayCamera(_Camera):
    def __init__(self, channel: _Literal["front", "left", "right", "rear"],
                 resolution: tuple[int, int] | None = None) -> None:
        super().__init__(-1, resolution)
        self._channel: _Literal["front", "left", "right", "rear"] = channel
        self._controller: ReplayController | None = None

    @_override
    def initialize(self, *parent_tags: str) -> None:
        _Device.initialize(self, *parent_tags)
        if not isinstance(controller := _get_controller(parent_tags[-1]), ReplayController):
            raise TypeError("Emulated cameras must be initialized with a replay controller")
        self._controller = controller

    @_override
    def read(self) -> _ndarray | None:
        return _array(self.read_pil())

    @_override
    def read_pil(self) -> _Image | None:
        if not isinstance(dc := self._controller.current_data_container(), _VisualDataContainer):
            raise TypeError("Emulated cameras require visual data containers")
        return _open(_BytesIO(_b64decode(getattr(dc, f"{self._channel}_view_base64"))))

    @_override
    def close(self) -> None:
        pass
