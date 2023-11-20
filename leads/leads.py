from typing import TypeVar as _TypeVar, Optional as _Optional, Any as _Any

from .context import Context
from .event import EventListener, UpdateEvent, SuspensionEvent, InterventionEvent, SYSTEM_DTCS

T = _TypeVar("T")


class Leads(Context[T]):
    def __init__(self, event_listener: EventListener = EventListener(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._event_listener: EventListener = event_listener

    def set_event_listener(self, event_listener: EventListener):
        self._event_listener = event_listener

    def _require_data(self, name: str) -> _Optional[_Any]:
        try:
            return self.data().__getattr__(name)
        except AttributeError:
            self._event_listener.on_suspend(SuspensionEvent(self, "DTCS", f"no data for `{name}`"))

    def update(self):
        self._event_listener.on_update(UpdateEvent(self))

        if front_wheel_speed := self._require_data("front_wheel_speed"):
            # DTCS
            if self.is_dtcs_enabled() and self.in_srw_mode() and (rear_wheel_speed := self._require_data("rear_wheel_speed")):
                if front_wheel_speed < rear_wheel_speed:
                    self._event_listener.on_intervene(InterventionEvent(self,
                                                                        SYSTEM_DTCS,
                                                                        front_wheel_speed,
                                                                        rear_wheel_speed))
            if self.is_dtcs_enabled() and not self.in_srw_mode() and (left_rear_wheel_speed := self._require_data("left_rear_wheel_speed")):
                if front_wheel_speed < left_rear_wheel_speed:
                    self._event_listener.on_intervene(InterventionEvent(self,
                                                                        SYSTEM_DTCS,
                                                                        "l",
                                                                        front_wheel_speed,
                                                                        left_rear_wheel_speed))
            if self.is_dtcs_enabled() and not self.in_srw_mode() and (right_rear_wheel_speed := self._require_data("right_rear_wheel_speed")):
                if front_wheel_speed < right_rear_wheel_speed:
                    self._event_listener.on_intervene(InterventionEvent(self,
                                                                        SYSTEM_DTCS,
                                                                        "r",
                                                                        front_wheel_speed,
                                                                        right_rear_wheel_speed))
