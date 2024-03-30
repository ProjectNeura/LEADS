import sys as _sys
from threading import Lock as _Lock
from types import FrameType as _FrameType

if hasattr(_sys, "_getframe"):
    def _currentframe() -> _FrameType:
        return getattr(_sys, "_getframe")(1)
else:
    def _currentframe() -> _FrameType:
        try:
            raise Exception
        except Exception as exc:
            return exc.__traceback__.tb_frame.f_back


class _ThreadFlags(object):
    def __init__(self) -> None:
        self._lock: _Lock = _Lock()
        self._active: bool = True

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, active: bool) -> None:
        self._lock.acquire()
        try:
            self._active = active
        finally:
            self._lock.release()


_thread_flags: _ThreadFlags = _ThreadFlags()
