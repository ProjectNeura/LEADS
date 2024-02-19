from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from typing import Any as _Any

from leads.context import Context


class Plugin(object, metaclass=_ABCMeta):
    def __init__(self) -> None:
        self.state: dict[str, _Any] = {}
        self.enabled: bool = True

    def __getitem__(self, key: str) -> _Any:
        return self.state[key]

    def __setitem__(self, key: str, value: _Any) -> None:
        self.state[key] = value

    @_abstractmethod
    def on_update(self, context: Context) -> None:
        raise NotImplementedError
