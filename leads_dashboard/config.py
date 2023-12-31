from json import load as _load, dumps as _dumps
from typing import TextIO as _TextIO, Any as _Any

from leads_dashboard.system import get_system_platform


class Config(object):
    def __init__(self, base: dict[str, _Any]) -> None:
        """
        :param base: base dictionary
        """
        self._d: dict[str, _Any] = base
        self.srw_mode: bool = True
        self.width: int = 720
        self.height: int = 480
        self.fullscreen: bool = False
        self.no_title_bar: bool = False
        self.refresh_rate: int = 30
        self.font_size_small: int = 8
        self.font_size_medium: int = 16
        self.font_size_large: int = 32
        self.font_size_x_large: int = 48
        self.scaling_factor: float = .8 if get_system_platform() == "linux" else 1
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

    def __str__(self) -> str:
        return _dumps(self)

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
