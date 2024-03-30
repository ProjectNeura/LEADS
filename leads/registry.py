from typing import TypeVar as _TypeVar

from leads.context import Context
from leads.types import OnRegister as _OnRegister, OnRegisterChain as _OnRegisterChain

T = _TypeVar("T", bound=Context)

_context_instance: T | None = None

_on_register_context: _OnRegister[T] = lambda _: None


def set_on_register_context(callback: _OnRegisterChain[T]) -> None:
    global _on_register_context
    _on_register_context = callback(_on_register_context)


def register_context(context: T) -> None:
    global _context_instance
    if _context_instance:
        raise RuntimeError("Another context is already registered")
    _on_register_context(context)
    _context_instance = context


def get_context() -> T | None:
    return _context_instance


def require_context() -> T:
    if _context_instance:
        return _context_instance
    raise RuntimeError("No context registered")
