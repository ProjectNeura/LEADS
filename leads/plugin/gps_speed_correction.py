from typing import Any as _Any, override as _override

from leads import Context
from leads.plugin.plugin import Plugin


class GPSSpeedCorrection(Plugin):
    def __init__(self) -> None:
        super().__init__(["speed", "gps_valid", "gps_ground_speed"])

    @_override
    def on_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        pass
