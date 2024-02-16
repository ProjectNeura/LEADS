from enum import StrEnum as _StrEnum


class System(_StrEnum):
    DTCS: str = "DTCS"
    ABS: str = "ABS"
    EBI: str = "EBI"
    ATBS: str = "ATBS"
    COMM: str = "COMM"
