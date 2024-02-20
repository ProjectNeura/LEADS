from typing import Any as _Any

from leads.constant import SystemLiteral
from leads.context import Context
from leads.event import InterventionEvent, InterventionExitEvent
from leads.plugin.plugin import Plugin
from leads.types import OptionalNumber


def dtcs_srw(context: Context,
             front_wheel_speed: OptionalNumber,
             rear_wheel_speed: OptionalNumber) -> InterventionEvent:
    if front_wheel_speed < rear_wheel_speed:
        context.overwrite_throttle(0)
        return InterventionEvent(context, SystemLiteral.DTCS, front_wheel_speed, rear_wheel_speed)
    return InterventionExitEvent(context, SystemLiteral.DTCS, front_wheel_speed, rear_wheel_speed)


def dtcs_drw(context: Context,
             front_wheel_speed: OptionalNumber,
             left_rear_wheel_speed: OptionalNumber,
             right_rear_wheel_speed: OptionalNumber) -> InterventionEvent:
    if front_wheel_speed < left_rear_wheel_speed:
        context.overwrite_throttle(0)
        return InterventionEvent(context, SystemLiteral.DTCS, "l", front_wheel_speed, left_rear_wheel_speed)
    if front_wheel_speed < right_rear_wheel_speed:
        context.overwrite_throttle(0)
        return InterventionEvent(context, SystemLiteral.DTCS, "r", front_wheel_speed, right_rear_wheel_speed)
    return InterventionExitEvent(context, SystemLiteral.DTCS,
                                 front_wheel_speed, left_rear_wheel_speed, right_rear_wheel_speed)


class DTCS(Plugin):
    def __init__(self):
        super(DTCS, self).__init__((["front_wheel_speed", "rear_wheel_speed"],
                                    ["front_wheel_speed", "left_rear_wheel_speed", "right_rear_wheel_speed"]))

    def on_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        context.intervene(dtcs_srw(context, kwargs["front_wheel_speed"], kwargs["rear_wheel_speed"])
                          if context.srw_mode() else
                          dtcs_drw(context, kwargs["front_wheel_speed"], kwargs["left_rear_wheel_speed"],
                                   kwargs["right_rear_wheel_speed"]))
