from typing import Callable as _Callable, SupportsInt as _SupportsInt, SupportsFloat as _SupportsFloat

type Number = int | float | _SupportsInt | _SupportsFloat
type Compressor[T] = _Callable[[list[T], int], list[T]]
type OnRegister[T] = _Callable[[T], None]
type OnRegisterChain[T] = _Callable[[OnRegister[T]], OnRegister[T]]
