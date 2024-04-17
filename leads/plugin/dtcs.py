from typing import Any as _Any, override as _override

from leads.constant import SystemLiteral
from leads.context import Context
from leads.event import InterventionEvent, InterventionExitEvent
from leads.plugin.plugin import Plugin


def do_dtcs(context: Context,
            front_wheel_speed: float,
            rear_wheel_speed: float) -> InterventionEvent:
    if front_wheel_speed < rear_wheel_speed:
        d = context.data()
        d.throttle = 0
        return InterventionEvent(context, SystemLiteral.DTCS, front_wheel_speed, rear_wheel_speed)
    return InterventionExitEvent(context, SystemLiteral.DTCS, front_wheel_speed, rear_wheel_speed)


class DTCS(Plugin):
    def __init__(self) -> None:
        super(DTCS, self).__init__(("front_wheel_speed", "rear_wheel_speed"))

    @_override
    def pre_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        context.intervene(do_dtcs(context, kwargs["front_wheel_speed"], kwargs["rear_wheel_speed"]))
