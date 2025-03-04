from typing import override as _override

from leads import Device as _Device


class Pedal(_Device):
    """
    See LEADS-Arduino.

    Supports:
    - Any analog pedal
    """

    def __init__(self) -> None:
        super().__init__()
        self._position: float = 0

    @_override
    def update(self, data: str) -> None:
        self._position = float(data)

    @_override
    def read(self) -> float:
        """
        :return: pedal position that ranges from 0 to 1
        """
        return self._position
