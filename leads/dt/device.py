from abc import abstractmethod as _abstractmethod, ABCMeta as _ABCMeta
from threading import Thread as _Thread
from typing import Any as _Any, override as _override, overload as _overload

from leads.os import _thread_flags


class Device(object):
    @_overload
    def __init__(self, *args, **kwargs) -> None:  # real signature unknown
        raise NotImplementedError

    def __init__(self, *pins: int | str) -> None:
        self._tag: str = ""
        self._parent_tags: tuple[str, ...] = ()
        self._pins: tuple[int | str, ...] = pins

    def level(self) -> int:
        """
        Get the level of the device in the device tree.
        :return: the number of parents
        """
        return len(self._parent_tags)

    def tag(self, tag: str | None = None) -> str | None:
        """
        Set or get the tag of the device.
        :param tag: the tag or None if getter mode
        :return: the tag or None if setter mode
        """
        if tag is None:
            return self._tag
        self._tag = tag

    def parent_tags(self) -> tuple[str, ...]:
        """
        Get the parent tags of the device.
        :return: the parent tags
        """
        return self._parent_tags[:]

    def pins_check(self, required_num: int) -> None:
        if len(self._pins) != required_num:
            raise ValueError(f"`{self.__class__.__name__}` only takes in {required_num} pins")

    def initialize(self, *parent_tags: str) -> None:
        self._parent_tags = parent_tags

    def read(self) -> _Any:
        raise NotImplementedError

    def write(self, payload: _Any) -> None:
        raise NotImplementedError

    def update(self, data: _Any) -> None:
        raise NotImplementedError

    def close(self) -> None:
        ...


class ShadowDevice(Device, metaclass=_ABCMeta):
    def __init__(self, *pins: int | str) -> None:
        super().__init__(*pins)
        self._shadow_thread: _Thread | None = None

    @_abstractmethod
    def loop(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        while _thread_flags.active:
            self.loop()

    @_override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        self._shadow_thread = _Thread(name=f"{id(self)} shadow", target=self.run, daemon=True)
        self._shadow_thread.start()
