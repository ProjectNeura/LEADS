from typing import override as _override

from gpiozero import CPUTemperature as _CPUTemperature

from leads import Device as _Device


class CPUMonitor(_Device):
    def __init__(self) -> None:
        super().__init__()
        self._cpu_temp: _CPUTemperature = _CPUTemperature()

    @_override
    def read(self) -> dict[str, float]:
        return {"temp": self._cpu_temp.temperature}
