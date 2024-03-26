from typing import Callable as _Callable, SupportsInt as _SupportsInt, SupportsFloat as _SupportsFloat

type Number = int | float | _SupportsInt | _SupportsFloat
type OptionalSpeed = float | None
type Compressor[T] = _Callable[[list[T], int], list[T]]
type Stringifier[T] = _Callable[[T], str]
type RequiredData = list[str] | tuple[list[str], list[str]]
type OnRegister[T] = _Callable[[T], None]
type OnRegisterChain[T] = _Callable[[OnRegister[T]], OnRegister[T]]
