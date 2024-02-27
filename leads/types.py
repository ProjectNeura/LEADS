from typing import Callable as _Callable

type OptionalSpeed = float | None
type Compressor[T] = _Callable[[list[T], int], list[T]]
type Stringifier[T] = _Callable[[T], str]
type RequiredData = list[str] | tuple[list[str], list[str]]
type OnRegisterConfig[T] = _Callable[[T], None]
type OnRegisterConfigChain[T] = _Callable[[OnRegisterConfig[T] | None], OnRegisterConfig[T]]
