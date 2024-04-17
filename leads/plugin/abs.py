from typing import Any as _Any, override as _override

from leads.constant import SystemLiteral
from leads.context import Context
from leads.event import InterventionEvent, InterventionExitEvent
from leads.plugin.plugin import Plugin


def do_abs(context: Context,
           front_wheel_speed: float,
           rear_wheel_speed: float) -> InterventionEvent:
    if front_wheel_speed > rear_wheel_speed:
        d = context.data()
        d.brake = 0
        return InterventionEvent(context, SystemLiteral.ABS, front_wheel_speed, rear_wheel_speed)
    return InterventionExitEvent(context, SystemLiteral.ABS, front_wheel_speed, rear_wheel_speed)


class ABS(Plugin):
    def __init__(self) -> None:
        super(ABS, self).__init__(("front_wheel_speed", "rear_wheel_speed"))

    @_override
    def pre_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        context.intervene(do_abs(context, kwargs["front_wheel_speed"], kwargs["rear_wheel_speed"]))
