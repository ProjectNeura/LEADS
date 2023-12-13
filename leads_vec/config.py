from json import load as _load, loads as _loads
from typing import TextIO as _TextIO, Any as _Any


class Config(object):
    def __init__(self, base: dict[str, _Any]) -> None:
        self._d: dict[str, _Any] = base

    def __getitem__(self, name: str) -> _Any | None:
        return self._d.get(name, None)

    def __getattr__(self, name: str) -> _Any | None:
        return self[name]

    def require(self, name: str) -> _Any:
        if r := self[name] is None:
            raise KeyError(name)
        return r


def load_config(file: str | _TextIO) -> Config:
    return Config(_loads(file) if isinstance(file, str) else _load(file))
