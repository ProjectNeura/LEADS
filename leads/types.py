from typing import Callable as _Callable, SupportsInt as _SupportsInt, SupportsFloat as _SupportsFloat

type Number = int | float | _SupportsInt | _SupportsFloat
type Compressor[T] = _Callable[[list[T], int], list[T]]
type OnRegister[T] = _Callable[[T], None]
type OnRegisterChain[T] = _Callable[[OnRegister[T]], OnRegister[T]]
type SupportedConfigValue = bool | int | float | str | None
type SupportedConfig = SupportedConfigValue | tuple[SupportedConfig, ...]
type VisualHeader = tuple[
    str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str]
type VisualHeaderFull = tuple[
    str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str]
