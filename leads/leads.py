from typing import TypeVar as _TypeVar, Any as _Any

from leads.constant import SYSTEM_DTCS, SYSTEM_ABS, SYSTEM_EBI, SYSTEM_ATBS
from leads.context import Context
from leads.event import EventListener, DataPushedEvent, UpdateEvent, SuspensionEvent, InterventionEvent, \
    InterventionExitEvent
from leads.data import DataContainer

T = _TypeVar("T", bound=DataContainer)

_OptionalNumber = int | float | None


def dtcs_srw(context: Context,
             front_wheel_speed: _OptionalNumber,
             rear_wheel_speed: _OptionalNumber) -> InterventionEvent:
    if rear_wheel_speed and front_wheel_speed < rear_wheel_speed:
        return InterventionEvent(context, SYSTEM_DTCS, front_wheel_speed, rear_wheel_speed)
    return InterventionExitEvent(context, SYSTEM_DTCS, front_wheel_speed, rear_wheel_speed)


def dtcs_drw(context: Context,
             front_wheel_speed: _OptionalNumber,
             left_rear_wheel_speed: _OptionalNumber,
             right_rear_wheel_speed: _OptionalNumber) -> InterventionEvent:
    if left_rear_wheel_speed and front_wheel_speed < left_rear_wheel_speed:
        return InterventionEvent(context, SYSTEM_DTCS, "l", front_wheel_speed, left_rear_wheel_speed)
    if right_rear_wheel_speed and front_wheel_speed < right_rear_wheel_speed:
        return InterventionEvent(context, SYSTEM_DTCS, "r", front_wheel_speed, right_rear_wheel_speed)
    return InterventionExitEvent(context, SYSTEM_DTCS, front_wheel_speed, left_rear_wheel_speed, right_rear_wheel_speed)


class Leads(Context[T]):
    def __init__(self, event_listener: EventListener = EventListener(), *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._event_listener: EventListener = event_listener

    def set_event_listener(self, event_listener: EventListener) -> None:
        self._event_listener = event_listener

    def _acquire_data(self, name: str, *systems: str, mandatory: bool = True) -> _Any | None:
        try:
            return self.data().__getattribute__(name)
        except AttributeError:
            if mandatory:
                for system in systems:
                    self._event_listener.on_suspend(SuspensionEvent(self, system, f"no data for `{name}`"))

    def push(self, data: T) -> None:
        self._event_listener.on_push(DataPushedEvent(self, data))
        super().push(data)
        self._event_listener.post_push(DataPushedEvent(self, data))

    def intervene(self, event: InterventionEvent) -> None:
        if isinstance(event, InterventionExitEvent):
            self._event_listener.post_intervene(event)
        else:
            self._event_listener.on_intervene(event)

    def update(self) -> None:
        self._event_listener.on_update(UpdateEvent(self))

        if front_wheel_speed := self._acquire_data("front_wheel_speed",
                                                   SYSTEM_DTCS,
                                                   SYSTEM_ABS,
                                                   SYSTEM_EBI,
                                                   SYSTEM_ATBS):
            rear_wheel_speed = self._acquire_data("rear_wheel_speed",
                                                  SYSTEM_DTCS, SYSTEM_ATBS,
                                                  mandatory=self.in_srw_mode())
            left_rear_wheel_speed = self._acquire_data("left_rear_wheel_speed",
                                                       SYSTEM_DTCS, SYSTEM_ATBS,
                                                       mandatory=not self.in_srw_mode())
            right_rear_wheel_speed = self._acquire_data("right_rear_wheel_speed",
                                                        SYSTEM_DTCS, SYSTEM_ATBS,
                                                        mandatory=not self.in_srw_mode())
            # DTCS
            if self.is_dtcs_enabled():
                if self.in_srw_mode():
                    self.intervene(dtcs_srw(self, front_wheel_speed, rear_wheel_speed))
                else:
                    self.intervene(dtcs_drw(self, front_wheel_speed, left_rear_wheel_speed, right_rear_wheel_speed))

        self._event_listener.post_update(UpdateEvent(self))

    def brake(self, force: float) -> int:
        self.intervene(InterventionEvent(self, "BRAKING", force))
        try:
            return super().brake(force)
        finally:
            self.intervene(InterventionExitEvent(self, "BRAKING", force))
