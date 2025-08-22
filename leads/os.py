from atexit import register as _register
from threading import Lock as _Lock
from types import FrameType as _FrameType


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
        with self._lock:
            self._active = active


_thread_flags: _ThreadFlags = _ThreadFlags()


@_register
def _request_threads_stop() -> None:
    _thread_flags.active = False
