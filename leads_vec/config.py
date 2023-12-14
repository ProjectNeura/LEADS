from json import load as _load
from typing import TextIO as _TextIO, Any as _Any, Self as _Self


class Config(object):
    def __init__(self, base: dict[str, _Any]) -> None:
        self._d: dict[str, _Any] = base
        self.srw_mode: bool = True
        self.analysis_rate: float = .01
        self.update_rate: float = .25
        self.comm_addr: str = "127.0.0.1"
        self.comm_port: int = 16900
        self.data_dir: str = "./data"

    def __getitem__(self, name: str) -> _Any | None:
        return self.get(name)

    def __getattr__(self, name: str) -> _Any | None:
        return self.get(name)

    def get(self, name: str, default: _Any | None = None) -> _Any:
        if r := self._d.get(name):
            return r
        return default

    def load(self) -> _Self:
        for name in dir(self):
            if not name.startswith("_") and (v := self.get(name)):
                self.__setattr__(name, v)
        return self


DEFAULT_CONFIG = Config({})


def load_config(file: str | _TextIO) -> Config:
    return Config(_load(open(file, "r")) if isinstance(file, str) else _load(file)).load()
