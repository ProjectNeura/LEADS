from json import load as _load
from typing import TypeVar as _TypeVar, TextIO as _TextIO, Callable as _Callable, Any as _Any

from leads.config.template import ConfigTemplate

T = _TypeVar("T", bound=ConfigTemplate)


_config_instance: T | None = None


def load_config(file: str | _TextIO, constructor: _Callable[[dict[str, _Any]], T]) -> T:
    if isinstance(file, str):
        with open(file) as f:
            return constructor(_load(f))
    return constructor(_load(file))


def register_config(config: T | None) -> None:
    global _config_instance
    if config and _config_instance:
        raise RuntimeError("Another config is already registered")
    _config_instance = config


def get_config(constructor: _Callable[[dict[str, _Any]], T]) -> T:
    if not _config_instance:
        return constructor({})
    return _config_instance
