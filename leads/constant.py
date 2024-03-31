from enum import StrEnum as _StrEnum, IntEnum as _IntEnum


class SystemLiteral(_StrEnum):
    DTCS: str = "DTCS"
    ABS: str = "ABS"
    EBI: str = "EBI"
    ATBS: str = "ATBS"


class ESCMode(_IntEnum):
    STANDARD: int = 0
    AGGRESSIVE: int = 1
    SPORT: int = 2
    OFF: int = 3
