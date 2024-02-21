from typing import TypeVar as _TypeVar, Any as _Any, override as _override

from leads.context import Context
from leads.data import DataContainer
from leads.event import EventListener, DataPushedEvent, UpdateEvent, SuspensionEvent, InterventionEvent, \
    InterventionExitEvent
from leads.plugin import Plugin

T = _TypeVar("T", bound=DataContainer)


class LEADS(Context[T]):
    def __init__(self, event_listener: EventListener = EventListener(), *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._plugins: dict[str, Plugin] = {}
        self._event_listener: EventListener = event_listener

    def plugin(self, key: str, plugin: Plugin | None = None) -> Plugin | None:
        if plugin:
            plugin.bind_context(self)
            self._plugins[key] = plugin
            plugin.load()
        else:
            return self._plugins[key]

    def set_event_listener(self, event_listener: EventListener) -> None:
        self._event_listener = event_listener

    @_override
    def suspend(self, event: SuspensionEvent) -> None:
        self._event_listener.on_suspend(event)

    def _acquire_data(self, name: str, *systems: str, mandatory: bool = True) -> _Any | None:
        try:
            return self.data().__getattribute__(name)
        except AttributeError:
            if mandatory:
                for system in systems:
                    self.suspend(SuspensionEvent(self, system, f"no data for `{name}`"))

    @_override
    def push(self, data: T) -> None:
        self._event_listener.on_push(DataPushedEvent(self, data))
        super().push(data)
        self._event_listener.post_push(DataPushedEvent(self, data))

    @_override
    def intervene(self, event: InterventionEvent) -> None:
        if isinstance(event, InterventionExitEvent):
            self._event_listener.post_intervene(event)
        else:
            self._event_listener.on_intervene(event)

    @_override
    def update(self) -> None:
        self._event_listener.on_update(UpdateEvent(self))

        for key, plugin in self._plugins.items():
            if plugin.enabled:
                plugin.update({d: self._acquire_data(d, key) for d in plugin.required_data()})

        self._event_listener.post_update(UpdateEvent(self))

    @_override
    def record_lap(self) -> None:
        self.intervene(InterventionEvent(self, "LAP RECORDING"))
        super().record_lap()
        return self.intervene(InterventionExitEvent(self, "LAP RECORDING"))

    @_override
    def overwrite_throttle(self, force: float) -> float:
        self.intervene(InterventionEvent(self, "THROTTLE", force))
        try:
            return super().overwrite_throttle(force)
        finally:
            self.intervene(InterventionExitEvent(self, "THROTTLE", force))

    @_override
    def overwrite_brake(self, force: float) -> float:
        self.intervene(InterventionEvent(self, "BRAKE", force))
        try:
            return super().overwrite_brake(force)
        finally:
            self.intervene(InterventionExitEvent(self, "BRAKE", force))
