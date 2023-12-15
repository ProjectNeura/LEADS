from json import load as _load
from typing import TextIO as _TextIO, Any as _Any


class Config(object):
    def __init__(self, base: dict[str, _Any]) -> None:
        """
        :param base: base dictionary
        """
        self._d: dict[str, _Any] = base
        self.srw_mode: bool = True
        self.analysis_rate: float = .01
        self.update_rate: float = .25
        self.comm_addr: str = "127.0.0.1"
        self.comm_port: int = 16900
        self.data_dir: str = "./data"
        self.refresh()

    def __getitem__(self, name: str) -> _Any | None:
        return self.get(name)

    def __getattr__(self, name: str) -> _Any | None:
        return self.get(name)

    def __setitem__(self, name: str, value: _Any) -> None:
        self._d[name] = value
        self.refresh()

    def load(self, d: dict[str, _Any]) -> None:
        """
        Load a new dictionary and refresh.
        :param d: the dictionary to load
        """
        self._d = d
        self.refresh()

    def get(self, name: str, default: _Any | None = None) -> _Any:
        """
        Get the value of a given name from the dictionary.
        :param name: dictionary key
        :param default: default value if the value does not exist
        :return: the value if it exists or else the default value
        """
        if r := self._d.get(name):
            return r
        return default

    def refresh(self) -> None:
        """
        Write the dictionary into the instance attributes.
        """
        for name in dir(self):
            if not name.startswith("_") and (v := self.get(name)):
                self.__setattr__(name, v)


DEFAULT_CONFIG = Config({})


def load_config(file: str | _TextIO) -> Config:
    return Config(_load(open(file)) if isinstance(file, str) else _load(file))
