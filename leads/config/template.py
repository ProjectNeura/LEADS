from json import dumps as _dumps
from typing import override as _override, Literal as _Literal, Any as _Any

from leads.data import Serializable
from leads.types import SupportedConfig as _SupportedConfig


class ConfigTemplate(Serializable):
    def __init__(self, base: dict[str, _SupportedConfig]) -> None:
        """
        All custom attributes should be public (not named after "_").
        Writable attributes should start with "w_" such as "w_debug_level".
        :param base: the base dictionary
        """
        self._d: dict[str, _SupportedConfig] = self.fix_dict(base)
        self._frozen: bool = False
        self.w_debug_level: _Literal["DEBUG", "INFO", "WARN", "ERROR"] = "DEBUG"
        self.data_seq_size: int = 100
        self.num_laps_timed: int = 3
        self.refresh()

    def fix_dict(self, d: dict[str, _Any]) -> dict[str, _SupportedConfig]:
        return {k: self.fix_type(v) for k, v in d.items()}

    def fix_type(self, value: _Any) -> _SupportedConfig:
        if isinstance(value, (tuple, list)):
            return tuple(self.fix_type(i) for i in value)
        if not isinstance(value, (bool, int, float, str, type(None))):
            raise TypeError(f"Unsupported value type: {value}")
        return value

    def __getitem__(self, name: str) -> _SupportedConfig | None:
        return self.get(name)

    def __setitem__(self, name: str, value: _SupportedConfig) -> None:
        self.set(name, value)

    @_override
    def __setattr__(self, name: str, value: _SupportedConfig) -> None:
        if self._writable(name):
            super().__setattr__(name, value if name.startswith("_") else self.fix_type(value))

    @_override
    def __str__(self) -> str:
        """
        Convert to a JSON string.
        :return: the JSON string
        """
        return _dumps(self.to_dict())

    @_override
    def to_dict(self) -> dict[str, _SupportedConfig]:
        return self._d.copy()

    def _writable(self, name: str) -> bool:
        """
        :param name: the configuration name
        :return: True: writable; False: readonly
        """
        return not hasattr(self, "_frozen") or not self._frozen or name.startswith("w_")

    def set(self, name: str, value: _SupportedConfig) -> None:
        """
        Set the value with the given name in the dictionary.
        :param name: the dictionary key
        :param value: the value to set
        """
        if self._writable(name):
            self._d[name] = self.fix_type(value)
            self.refresh()

    def get(self, name: str, default: _SupportedConfig | None = None) -> _SupportedConfig | None:
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
