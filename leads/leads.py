from typing import TypeVar as _TypeVar, Any as _Any, override as _override, Literal as _Literal

from leads.context import Context
from leads.data import DataContainer
from leads.event import EventListener, DataPushedEvent, UpdateEvent, SuspensionEvent, InterventionEvent, \
    InterventionExitEvent
from leads.plugin import Plugin

T = _TypeVar("T", bound=DataContainer)


class LEADS(Context[T]):
    _plugins: dict[tuple[str, ...], Plugin] = {}
    _event_listener: EventListener = EventListener()

    def plugin(self, key: str | tuple[str, ...], plugin: Plugin | None = None) -> Plugin | None:
        if isinstance(key, str):
            key = key,
        if plugin is None:
            return self._plugins[key]
        self._plugins[key] = plugin
        plugin.on_load(self)

    def set_event_listener(self, event_listener: EventListener) -> None:
        event_listener.bind_chain(self._event_listener)
        self._event_listener = event_listener

    @_override
    def suspend(self, event: SuspensionEvent) -> None:
        self._event_listener.pre_suspend(event)

    def _acquire_data(self, name: str, *systems: str, mandatory: bool = True) -> _Any | None:
        try:
            return getattr(self.data(), name)
        except AttributeError:
            if mandatory:
                for system in systems:
                    self.suspend(SuspensionEvent(self, system, f"no data for `{name}`"))

    def _do_plugin_callback(self, method: _Literal["pre_push", "post_push", "pre_update", "post_update"]) -> None:
        for key, plugin in self._plugins.items():
            if plugin.enabled():
                getattr(plugin, method)(self, {d: self._acquire_data(d, *key) for d in plugin.required_data()})

    @_override
    def push(self, data: T) -> None:
        self._event_listener.pre_push(DataPushedEvent(self, data))
        self._do_plugin_callback("pre_push")
        super().push(data)
        self._do_plugin_callback("post_push")
        self._event_listener.post_push(DataPushedEvent(self, data))

    @_override
    def intervene(self, event: InterventionEvent) -> None:
        if isinstance(event, InterventionExitEvent):
            self._event_listener.post_intervene(event)
        else:
            self._event_listener.pre_intervene(event)

    @_override
    def update(self) -> None:
        self._do_plugin_callback("pre_update")
        self._event_listener.on_update(UpdateEvent(self))
        self._do_plugin_callback("post_update")

    @_override
    def time_lap(self) -> None:
        self.intervene(InterventionEvent(self, "LAP RECORDING"))
        super().time_lap()
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
