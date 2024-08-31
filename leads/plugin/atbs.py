from typing import override as _override, Any as _Any

from leads.constant import SystemLiteral
from leads.context import Context
from leads.dt import THROTTLE_PEDAL, BRAKE_PEDAL
from leads.event import InterventionEvent, InterventionExitEvent
from leads.plugin.plugin import ESCPlugin


def do_atbs(context: Context) -> InterventionEvent:
    return InterventionExitEvent(context, SystemLiteral.ATBS)


class ATBS(ESCPlugin):
    def __init__(self) -> None:
        super().__init__((), (THROTTLE_PEDAL, BRAKE_PEDAL))

    @_override
    def pre_update(self, context: Context, kwargs: dict[str, _Any]) -> None:
        context.intervene(do_atbs(context))
