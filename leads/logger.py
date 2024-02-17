from datetime import datetime as _datetime
from enum import IntEnum as _IntEnum


class Level(_IntEnum):
    INFO: int = 0x00
    DEBUG: int = 0x01
    WARN: int = 0x02
    ERROR: int = 0x03


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
        self._debug_level: Level = Level.INFO

    def debug_level(self, debug_level: Level | None = None) -> Level | None:
        if debug_level:
            self._debug_level = debug_level
        else:
            return self._debug_level

    @staticmethod
    def mark(msg: str, level: Level) -> str:
        return f"[{repr(level)[1:-1]}] [{_datetime.now()}] {msg}"

    @staticmethod
    def format(msg: str, font: int, color: int | None, background: int | None) -> str:
        return f"\033[{font}{f";{color}" if color else ""}{f";{background + 10}" if background else ""}m{msg}\033[0m"

    def print(self, msg: str, level: int) -> None:
        if self._debug_level <= level:
            print(msg)

    def info(self, *msg: str, sep: str = " ", end: str = "\n",
             f: tuple[int, int | None, int | None] = (REGULAR, None, None)):
        self.print(self.format(self.mark(sep.join(msg) + end, level=Level.INFO), *f), Level.INFO)

    def debug(self, *msg: str, sep: str = " ", end: str = "\n",
              f: tuple[int, int | None, int | None] = (REGULAR, YELLOW, None)):
        self.print(self.format(self.mark(sep.join(msg) + end, level=Level.DEBUG), *f), Level.DEBUG)

    def warn(self, *msg: str, sep: str = " ", end: str = "\n",
             f: tuple[int, int | None, int | None] = (REGULAR, RED, None)):
        self.print(self.format(self.mark(sep.join(msg) + end, level=Level.WARN), *f), Level.WARN)

    def error(self, *msg: str, sep: str = " ", end: str = "\n",
              f: tuple[int, int | None, int | None] = (REGULAR, RED, None)):
        self.print(self.format(self.mark(sep.join(msg) + end, Level.ERROR), *f), Level.ERROR)


L: Logger = Logger()
