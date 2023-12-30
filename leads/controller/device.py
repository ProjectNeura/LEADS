from abc import abstractmethod as _abstractmethod, ABCMeta as _ABCMeta
from threading import Thread as _Thread
from typing import Any as _Any


class Device(object, metaclass=_ABCMeta):
    def __init__(self, tag: str, *pins: int | str) -> None:
        self._tag: str = tag
        self._pins: tuple[int | str, ...] = pins

    def tag(self) -> str:
        return self._tag

    def initialize(self) -> None:
        pass

    @_abstractmethod
    def read(self) -> _Any:
        raise NotImplementedError

    @_abstractmethod
    def write(self, payload: _Any) -> None:
        raise NotImplementedError


class ShadowDevice(Device, metaclass=_ABCMeta):
    def __init__(self, tag: str, *pins: int | str) -> None:
        super().__init__(tag, *pins)
        self._shadow_thread: _Thread | None = None

    @_abstractmethod
    def loop(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        while True:
            self.loop()

    def initialize(self) -> None:
        self._shadow_thread = _Thread(name=f"{self._tag} shadow", target=self.run)
        self._shadow_thread.start()
