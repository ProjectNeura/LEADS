from json import dumps as _dumps
from typing import Any as _Any, override as _override, Literal as _Literal

from leads.data import Serializable


class ConfigTemplate(Serializable):
    def __init__(self, base: dict[str, _Any]) -> None:
        """
        All custom attributes should be public (not named after "_").
        Writable attributes should start with "w_" such as "w_debug_level".
        :param base: the base dictionary
        """
        self._d: dict[str, _Any] = base
        self._frozen: bool = False
        self.w_debug_level: _Literal["DEBUG", "INFO", "WARN", "ERROR"] = "DEBUG"
        self.data_seq_size: int = 100
        self.num_laps_timed: int = 3
        self.data_dir: str = "data"
        self.refresh()

    def __getitem__(self, name: str) -> _Any | None:
        return self.get(name)

    def __setitem__(self, name: str, value: _Any) -> None:
        self.set(name, value)

    @_override
    def __setattr__(self, name: str, value: _Any) -> None:
        if self._writable(name):
            super().__setattr__(name, value)

    @_override
    def __str__(self) -> str:
        """
        Convert to a JSON string.
        :return: the JSON string
        """
        return _dumps(self.to_dict())

    @_override
    def to_dict(self) -> dict[str, _Any]:
        return self._d.copy()

    def load(self, d: dict[str, _Any]) -> None:
        """
        Load a new dictionary and refresh.
        :param d: the dictionary to load
        """
        self._d = d
        self.refresh()

    def _writable(self, name: str) -> bool:
        """
        :param name: the configuration name
        :return: True: writable; False: readonly
        """
        return not hasattr(self, "_frozen") or not self._frozen or name.startswith("_") or name.startswith("w_")

    def set(self, name: str, value: _Any) -> None:
        """
        Set the value with the given name in the dictionary.
        :param name: the dictionary key
        :param value: the value to set
        """
        if self._writable(name):
            self._d[name] = value
            self.refresh()

    def get(self, name: str, default: _Any | None = None) -> _Any | None:
        """
        Get the value of a given name from the dictionary.
        :param name: the dictionary key
        :param default: the default value if the value does not exist
        :return: the value if it exists or else the default value
        """
        return self._d.get(name, default)

    def refresh(self) -> None:
        """
        Write the dictionary into the instance attributes.
        """
        for name in dir(self):
            if not name.startswith("_") and (v := self._d.get(name)) is not None:
                if self._writable(name):
                    setattr(self, name, v)
        self._frozen = True
