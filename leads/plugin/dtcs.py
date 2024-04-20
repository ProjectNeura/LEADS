from typing import Any as _Any, override as _override

from leads.constant import SystemLiteral, ESCMode
from leads.context import Context
from leads.event import InterventionEvent, InterventionExitEvent
from leads.plugin.plugin import ESCPlugin

# (absolute, percentage)
_CALIBRATIONS: dict[ESCMode, tuple[float | None, float | None]] = {
    ESCMode.STANDARD: (1, .05),
    ESCMode.AGGRESSIVE: (4, .15),
    ESCMode.SPORT: (8, None),
    ESCMode.OFF: (None, None)
}


def do_dtcs(context: Context,
            front_wheel_speed: float,
            rear_wheel_speed: float) -> InterventionEvent:
    if ESCPlugin.adjudicate(rear_wheel_speed - front_wheel_speed, front_wheel_speed,
                            *_CALIBRATIONS[context.esc_mode()]):
        d = context.data()
        d.throttle = 0
        return InterventionEvent(context, SystemLiteral.DTCS, front_wheel_speed, rear_wheel_speed)
    return InterventionExitEvent(context, SystemLiteral.DTCS, front_wheel_speed, rear_wheel_speed)


class DTCS(ESCPlugin):
    def __init__(self) -> None:
        super(DTCS, self).__init__(("front_wheel_speed", "rear_wheel_speed"))

    @_override
    def pre_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        context.intervene(do_dtcs(context, kwargs["front_wheel_speed"], kwargs["rear_wheel_speed"]))
