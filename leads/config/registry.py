from json import load as _load
from typing import TypeVar as _TypeVar, TextIO as _TextIO

from leads.config.template import ConfigTemplate
from leads.types import OnRegister as _OnRegister, OnRegisterChain as _OnRegisterChain

T = _TypeVar("T", bound=ConfigTemplate)

_config_instance: T | None = None

_on_register_config: _OnRegister[T] = lambda _: None


def set_on_register_config(callback: _OnRegisterChain[T]) -> None:
    global _on_register_config
    _on_register_config = callback(_on_register_config)


def load_config(file: str | _TextIO, constructor: type[T]) -> T:
    if isinstance(file, str):
        with open(file) as f:
            return constructor(_load(f))
    return constructor(_load(file))


def register_config(config: T) -> None:
    global _config_instance
    if _config_instance:
        raise RuntimeError("Another config is already registered")
    _on_register_config(config)
    _config_instance = config


def get_config() -> T | None:
    return _config_instance


def require_config() -> T:
    if _config_instance:
        return _config_instance
    raise RuntimeError("No config registered")
