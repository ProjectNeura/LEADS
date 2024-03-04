from enum import StrEnum as _StrEnum, IntEnum as _IntEnum


class SystemLiteral(_StrEnum):
    DTCS: str = "DTCS"
    ABS: str = "ABS"
    EBI: str = "EBI"
    ATBS: str = "ATBS"


class ECSMode(_IntEnum):
    STANDARD: int = 0x00
    AGGRESSIVE: int = 0x01
    SPORT: int = 0x02
    OFF: int = 0x03
