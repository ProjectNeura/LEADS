from abc import abstractmethod as _abstractmethod, ABCMeta as _ABCMeta
from threading import Thread as _Thread
from typing import Any as _Any


class Device(object):
    def __init__(self, *pins: int | str) -> None:
        self._tag: str = ""
        self._parent_tags: list[str] = []
        self._pins: tuple[int | str, ...] = pins

    def tag(self, tag: str | None = None) -> str | None:
        if tag:
            self._tag = tag
        else:
            return self._tag

    def parent_tags(self, parent_tags: list[str] | None = None) -> list[str] | None:
        if parent_tags:
            if len(self._parent_tags) > 0:
                raise RuntimeError("Duplicated initialization")
            self._parent_tags = parent_tags
        else:
            return self._parent_tags[:]

    def pins_check(self, required_num: int) -> None:
        if len(self._pins) != required_num:
            raise ValueError(f"`{self.__class__.__name__}` only takes in {required_num} pins")

    def initialize(self, *parent_tags: str) -> None:
        pass

    def read(self) -> _Any:
        raise NotImplementedError

    def write(self, payload: _Any) -> None:
        raise NotImplementedError

    def update(self, data: _Any) -> None:
        raise NotImplementedError

    def close(self) -> None:
        pass


class ShadowDevice(Device, metaclass=_ABCMeta):
    def __init__(self, *pins: int | str) -> None:
        super().__init__(*pins)
        self._shadow_thread: _Thread | None = None

    @_abstractmethod
    def loop(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        while True:
            self.loop()

    def initialize(self, *parent_tags: str) -> None:
        self._shadow_thread = _Thread(name=str(id(self)) + " shadow", target=self.run)
        self._shadow_thread.start()
