from typing import Any as _Any, override as _override

from leads.constant import SystemLiteral
from leads.context import Context
from leads.event import InterventionEvent, InterventionExitEvent
from leads.plugin.plugin import Plugin
from leads.types import OptionalSpeed as _OptionalSpeed


def abs_srw(context: Context,
            front_wheel_speed: _OptionalSpeed,
            rear_wheel_speed: _OptionalSpeed) -> InterventionEvent:
    if front_wheel_speed > rear_wheel_speed:
        context.overwrite_brake(0)
        return InterventionEvent(context, SystemLiteral.ABS, front_wheel_speed, rear_wheel_speed)
    return InterventionExitEvent(context, SystemLiteral.ABS, front_wheel_speed, rear_wheel_speed)


def abs_drw(context: Context,
            front_wheel_speed: _OptionalSpeed,
            left_rear_wheel_speed: _OptionalSpeed,
            right_rear_wheel_speed: _OptionalSpeed) -> InterventionEvent:
    if front_wheel_speed > left_rear_wheel_speed:
        context.overwrite_brake(0)
        return InterventionEvent(context, SystemLiteral.ABS, "l", front_wheel_speed, left_rear_wheel_speed)
    if front_wheel_speed > right_rear_wheel_speed:
        context.overwrite_brake(0)
        return InterventionEvent(context, SystemLiteral.ABS, "r", front_wheel_speed, right_rear_wheel_speed)
    return InterventionExitEvent(context, SystemLiteral.ABS,
                                 front_wheel_speed, left_rear_wheel_speed, right_rear_wheel_speed)


class ABS(Plugin):
    def __init__(self) -> None:
        super(ABS, self).__init__((["front_wheel_speed", "rear_wheel_speed"],
                                   ["front_wheel_speed", "left_rear_wheel_speed", "right_rear_wheel_speed"]))

    @_override
    def pre_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        context.intervene(abs_srw(context, kwargs["front_wheel_speed"], kwargs["rear_wheel_speed"])
                          if context.srw_mode() else
                          abs_drw(context, kwargs["front_wheel_speed"], kwargs["left_rear_wheel_speed"],
                                  kwargs["right_rear_wheel_speed"]))
