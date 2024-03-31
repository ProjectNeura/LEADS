from datetime import datetime as _datetime
from enum import IntEnum as _IntEnum
from threading import Lock as _Lock

from leads.config import set_on_register_config, ConfigTemplate
from leads.os import _currentframe
from leads.types import OnRegister as _OnRegister


class Level(_IntEnum):
    DEBUG: int = 0
    INFO: int = 1
    WARN: int = 2
    ERROR: int = 3


class Logger(object):
    REGULAR: int = 0
    BOLD: int = 1
    ITALIC: int = 3
    UNDERLINED: int = 4
    INVERSE: int = 7

    BLACK: int = 30
    RED: int = 31
    GREEN: int = 32
    YELLOW: int = 33
    BLUE: int = 34
    PURPLE: int = 35
    CYAN: int = 36
    WHITE: int = 37

    def __init__(self) -> None:
        self._debug_level: Level = Level.DEBUG
        self._lock: _Lock = _Lock()

    def debug_level(self, debug_level: Level | None = None) -> Level | None:
        if debug_level is None:
            return self._debug_level
        self._debug_level = debug_level

    @staticmethod
    def mark(msg: str, level: Level) -> str:
        return f"[{repr(level)[1:-1]}] [{_currentframe().f_back.f_back.f_code.co_name}] [{_datetime.now()}] {msg}"

    @staticmethod
    def format(msg: str, font: int, color: int | None, background: int | None) -> str:
        return f"\033[{font}{f";{color}" if color else ""}{f";{background + 10}" if background else ""}m{msg}\033[0m"

    def print(self, msg: str, level: int) -> None:
        self._lock.acquire()
        try:
            if self._debug_level <= level:
                print(msg)
        finally:
            self._lock.release()

    def info(self, *msg: str, sep: str = " ", end: str = "\n",
             f: tuple[int, int | None, int | None] = (REGULAR, None, None)) -> None:
        self.print(Logger.format(Logger.mark(sep.join(msg) + end, level=Level.INFO), *f), Level.INFO)

    def debug(self, *msg: str, sep: str = " ", end: str = "\n",
              f: tuple[int, int | None, int | None] = (REGULAR, YELLOW, None)) -> None:
        self.print(Logger.format(Logger.mark(sep.join(msg) + end, level=Level.DEBUG), *f), Level.DEBUG)

    def warn(self, *msg: str, sep: str = " ", end: str = "\n",
             f: tuple[int, int | None, int | None] = (REGULAR, RED, None)) -> None:
        self.print(Logger.format(Logger.mark(sep.join(msg) + end, level=Level.WARN), *f), Level.WARN)

    def error(self, *msg: str, sep: str = " ", end: str = "\n",
              f: tuple[int, int | None, int | None] = (REGULAR, RED, None)) -> None:
        self.print(Logger.format(Logger.mark(sep.join(msg) + end, Level.ERROR), *f), Level.ERROR)


L: Logger = Logger()


def _on_register_config(chain: _OnRegister[ConfigTemplate]) -> _OnRegister[ConfigTemplate]:
    def _(config: ConfigTemplate) -> None:
        chain(config)
        L.debug_level(Level[config.w_debug_level])

    return _


set_on_register_config(_on_register_config)
