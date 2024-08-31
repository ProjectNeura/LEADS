from typing import Any as _Any, override as _override

from leads.constant import SystemLiteral, ESCMode
from leads.context import Context
from leads.dt import WHEEL_SPEED_CONTROLLER, THROTTLE_PEDAL, BRAKE_PEDAL
from leads.event import InterventionEvent, InterventionExitEvent
from leads.plugin.plugin import ESCPlugin

# (absolute, percentage)
_CALIBRATIONS: dict[ESCMode, tuple[float | None, float | None]] = {
    ESCMode.STANDARD: (.01, .001),
    ESCMode.AGGRESSIVE: (1, .01),
    ESCMode.SPORT: (2, None),
    ESCMode.OFF: (None, None)
}


def do_abs(context: Context,
           front_wheel_speed: float,
           rear_wheel_speed: float) -> InterventionEvent:
    if ESCPlugin.adjudicate(front_wheel_speed - rear_wheel_speed, rear_wheel_speed, *_CALIBRATIONS[context.esc_mode()]):
        d = context.data()
        d.brake = 0
        return InterventionEvent(context, SystemLiteral.ABS, front_wheel_speed, rear_wheel_speed)
    return InterventionExitEvent(context, SystemLiteral.ABS, front_wheel_speed, rear_wheel_speed)


class ABS(ESCPlugin):
    def __init__(self) -> None:
        super().__init__(("front_wheel_speed", "rear_wheel_speed"),
                         (WHEEL_SPEED_CONTROLLER, THROTTLE_PEDAL, BRAKE_PEDAL))

    @_override
    def pre_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        context.intervene(do_abs(context, kwargs["front_wheel_speed"], kwargs["rear_wheel_speed"]))
