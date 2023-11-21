from typing import TypeVar as _TypeVar, Optional as _Optional, Any as _Any

from .constant import SYSTEM_DTCS, SYSTEM_ABS, SYSTEM_EBI, SYSTEM_ATBS
from .context import Context
from .event import EventListener, DataPushedEvent, UpdateEvent, SuspensionEvent, InterventionEvent

T = _TypeVar("T")


class Leads(Context[T]):
    def __init__(self, event_listener: EventListener = EventListener(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._event_listener: EventListener = event_listener

    def set_event_listener(self, event_listener: EventListener):
        self._event_listener = event_listener

    def _acquire_data(self, name: str, *systems: str, mandatory: bool = True) -> _Optional[_Any]:
        try:
            return self.data().__getattribute__(name)
        except AttributeError:
            if mandatory:
                for system in systems:
                    self._event_listener.on_suspend(SuspensionEvent(self, system, f"no data for `{name}`"))

    def push(self, data: T):
        self._event_listener.on_push(DataPushedEvent(self))
        super().push(data)
        self._event_listener.post_push(DataPushedEvent(self))

    def update(self):
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
            intervened = [False, False, False, False]
            # DTCS
            if self.in_srw_mode():
                if self.is_dtcs_enabled():
                    if rear_wheel_speed and front_wheel_speed < rear_wheel_speed:
                        self._event_listener.on_intervene(InterventionEvent(self,
                                                                            SYSTEM_DTCS,
                                                                            front_wheel_speed,
                                                                            rear_wheel_speed))
                        intervened[0] = True
            else:
                if self.is_dtcs_enabled():
                    if left_rear_wheel_speed and front_wheel_speed < left_rear_wheel_speed:
                        self._event_listener.on_intervene(InterventionEvent(self,
                                                                            SYSTEM_DTCS,
                                                                            "l",
                                                                            front_wheel_speed,
                                                                            left_rear_wheel_speed))
                        intervened[0] = True
                    if right_rear_wheel_speed and front_wheel_speed < rear_wheel_speed:
                        self._event_listener.on_intervene(InterventionEvent(self,
                                                                            SYSTEM_DTCS,
                                                                            "r",
                                                                            front_wheel_speed,
                                                                            right_rear_wheel_speed))
                        intervened[0] = True
            if not intervened[0]:
                self._event_listener.post_intervene(InterventionEvent(self, SYSTEM_DTCS))
            if not intervened[1]:
                self._event_listener.post_intervene(InterventionEvent(self, SYSTEM_ABS))
            if not intervened[2]:
                self._event_listener.post_intervene(InterventionEvent(self, SYSTEM_EBI))
            if not intervened[3]:
                self._event_listener.post_intervene(InterventionEvent(self, SYSTEM_ATBS))

        self._event_listener.post_update(UpdateEvent(self))
