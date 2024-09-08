from json import load as _load
from typing import TypeVar as _TypeVar, TextIO as _TextIO, Callable as _Callable

from leads.config.template import ConfigTemplate
from leads.types import OnRegister as _OnRegister, OnRegisterChain as _OnRegisterChain, \
    SupportedConfig as _SupportedConfig

T = _TypeVar("T", bound=ConfigTemplate)

_config_instance: T | None = None

_on_register_config: _OnRegister[T] = lambda _: None


def set_on_register_config(callback: _OnRegisterChain[T]) -> None:
    """
    Set the root node of the callback chain that is triggered when a configuration is registered.
    :param callback: the callback interface
    """
    global _on_register_config
    _on_register_config = callback(_on_register_config)


def load_config(file: str | _TextIO, constructor: _Callable[[dict[str, _SupportedConfig]], T]) -> T:
    """
    Load a configuration from a file.
    :param file: the file to load from
    :param constructor: the constructor or an equivalent function
    :return: the configuration
    """
    if isinstance(file, str):
        with open(file) as f:
            return constructor(_load(f))
    return constructor(_load(file))


def register_config(config: T) -> None:
    """
    Register a configuration.
    :param config: the configuration
    :exception RuntimeError: duplicated registration
    """
    global _config_instance
    if _config_instance:
        raise RuntimeError("Another config is already registered")
    _on_register_config(config)
    _config_instance = config


def get_config() -> T | None:
    """
    Get the registered configuration.
    :return: the configuration if registered or else None
    """
    return _config_instance


def require_config() -> T:
    """
    Require the registered configuration.
    :return: the configuration
    :exception RuntimeError: no configuration is registered
    """
    if _config_instance:
        return _config_instance
    raise RuntimeError("No config registered")
