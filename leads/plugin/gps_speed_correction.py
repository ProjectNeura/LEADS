from typing import override as _override, Any as _Any

from leads.context import Context
from leads.plugin.plugin import Plugin


class GPSSpeedCorrection(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self._loss: float = 0
        self._abs_loss: float = 0
        self._n: int = 0

    @_override
    def post_push(self, context: Context, kwargs: dict[str, _Any]) -> None:
        d = context.data()
        if not d.gps_valid:
            return
        self._loss += (current_loss := d.speed - d.gps_ground_speed)
        self._abs_loss += abs(current_loss)
        self._n += 1
        if d.speed < 5 and current_loss < self._abs_loss / self._n:
            d.speed = d.gps_ground_speed + self._loss / self._n
