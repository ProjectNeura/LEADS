from typing import TypeVar as _TypeVar, Any as _Any

from leads.constant import SystemLiteral
from leads.context import Context
from leads.data import DataContainer
from leads.event import EventListener, DataPushedEvent, UpdateEvent, SuspensionEvent, InterventionEvent, \
    InterventionExitEvent

T = _TypeVar("T", bound=DataContainer)

_OptionalNumber = int | float | None


def dtcs_srw(context: Context,
             front_wheel_speed: _OptionalNumber,
             rear_wheel_speed: _OptionalNumber) -> InterventionEvent:
    if front_wheel_speed < rear_wheel_speed:
        context.overwrite_throttle(0)
        return InterventionEvent(context, SystemLiteral.DTCS, front_wheel_speed, rear_wheel_speed)
    return InterventionExitEvent(context, SystemLiteral.DTCS, front_wheel_speed, rear_wheel_speed)


def dtcs_drw(context: Context,
             front_wheel_speed: _OptionalNumber,
             left_rear_wheel_speed: _OptionalNumber,
             right_rear_wheel_speed: _OptionalNumber) -> InterventionEvent:
    if front_wheel_speed < left_rear_wheel_speed:
        context.overwrite_throttle(0)
        return InterventionEvent(context, SystemLiteral.DTCS, "l", front_wheel_speed, left_rear_wheel_speed)
    if front_wheel_speed < right_rear_wheel_speed:
        context.overwrite_throttle(0)
        return InterventionEvent(context, SystemLiteral.DTCS, "r", front_wheel_speed, right_rear_wheel_speed)
    return InterventionExitEvent(context, SystemLiteral.DTCS,
                                 front_wheel_speed, left_rear_wheel_speed, right_rear_wheel_speed)


def abs_srw(context: Context,
            front_wheel_speed: _OptionalNumber,
            rear_wheel_speed: _OptionalNumber) -> InterventionEvent:
    if front_wheel_speed > rear_wheel_speed:
        context.overwrite_brake(0)
        return InterventionEvent(context, SystemLiteral.ABS, front_wheel_speed, rear_wheel_speed)
    return InterventionExitEvent(context, SystemLiteral.ABS, front_wheel_speed, rear_wheel_speed)


def abs_drw(context: Context,
            front_wheel_speed: _OptionalNumber,
            left_rear_wheel_speed: _OptionalNumber,
            right_rear_wheel_speed: _OptionalNumber) -> InterventionEvent:
    if front_wheel_speed > left_rear_wheel_speed:
        context.overwrite_brake(0)
        return InterventionEvent(context, SystemLiteral.ABS, "l", front_wheel_speed, left_rear_wheel_speed)
    if front_wheel_speed > right_rear_wheel_speed:
        context.overwrite_brake(0)
        return InterventionEvent(context, SystemLiteral.ABS, "r", front_wheel_speed, right_rear_wheel_speed)
    return InterventionExitEvent(context, SystemLiteral.ABS,
                                 front_wheel_speed, left_rear_wheel_speed, right_rear_wheel_speed)


class LEADS(Context[T]):
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

        if (front_wheel_speed := self._acquire_data("front_wheel_speed",
                                                    SystemLiteral.DTCS,
                                                    SystemLiteral.ABS,
                                                    SystemLiteral.EBI,
                                                    SystemLiteral.ATBS)) is not None:
            rear_wheel_speed = self._acquire_data("rear_wheel_speed",
                                                  SystemLiteral.DTCS, SystemLiteral.ATBS,
                                                  mandatory=self.srw_mode())
            left_rear_wheel_speed = self._acquire_data("left_rear_wheel_speed",
                                                       SystemLiteral.DTCS, SystemLiteral.ATBS,
                                                       mandatory=not self.srw_mode())
            right_rear_wheel_speed = self._acquire_data("right_rear_wheel_speed",
                                                        SystemLiteral.DTCS, SystemLiteral.ATBS,
                                                        mandatory=not self.srw_mode())
            # DTCS
            if self._dtcs:
                self.intervene(dtcs_srw(self, front_wheel_speed, rear_wheel_speed) if self._srw_mode else
                               dtcs_drw(self, front_wheel_speed, left_rear_wheel_speed, right_rear_wheel_speed))
            # ABS
            if self._abs:
                self.intervene(abs_srw(self, front_wheel_speed, rear_wheel_speed) if self._srw_mode else
                               abs_drw(self, front_wheel_speed, left_rear_wheel_speed, right_rear_wheel_speed))

        self._event_listener.post_update(UpdateEvent(self))

    def record_lap(self) -> None:
        self.intervene(InterventionEvent(self, "LAP RECORDING"))
        super().record_lap()
        return self.intervene(InterventionExitEvent(self, "LAP RECORDING"))

    def overwrite_throttle(self, force: float) -> float:
        self.intervene(InterventionEvent(self, "THROTTLE", force))
        try:
            return super().overwrite_throttle(force)
        finally:
            self.intervene(InterventionExitEvent(self, "THROTTLE", force))

    def overwrite_brake(self, force: float) -> float:
        self.intervene(InterventionEvent(self, "BRAKE", force))
        try:
            return super().overwrite_brake(force)
        finally:
            self.intervene(InterventionExitEvent(self, "BRAKE", force))
