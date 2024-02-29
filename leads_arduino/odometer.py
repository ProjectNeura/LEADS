from typing import override as _override

from leads import Device as _Device


class Odometer(_Device):
    def __init__(self):
        super().__init__()
        self._milage: float = 0

    @_override
    def write(self, payload: float) -> None:
        self._milage = payload

    @_override
    def read(self) -> float:
        return self._milage
