import sys as _sys
from types import FrameType as _FrameType

if hasattr(_sys, "_getframe"):
    def currentframe() -> _FrameType:
        return _sys._getframe(1)
else:
    def currentframe() -> _FrameType:
        try:
            raise Exception
        except Exception as exc:
            return exc.__traceback__.tb_frame.f_back
