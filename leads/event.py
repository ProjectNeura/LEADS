from typing import Any as _Any, override as _override, overload as _overload

from leads.callback import CallbackChain
from leads.context import Context
from leads.data import DataContainer


class Event(object):
    @_overload
    def __init__(self, *args, **kwargs) -> None:  # real signature unknown
        raise NotImplementedError

    def __init__(self, t: str, context: Context) -> None:
        self.t: str = t
        self.context: Context = context

    @_override
    def __str__(self) -> str:
        return f"[{self.t}] {self.context.data()}"


class DataPushedEvent(Event):
    def __init__(self, context: Context, data: DataContainer) -> None:
        super().__init__("DATA PUSHED", context)
        self.data: DataContainer = data


class UpdateEvent(Event):
    def __init__(self, context: Context) -> None:
        super().__init__("UPDATE", context)


class SystemEvent(Event):
    def __init__(self, t: str, context: Context, system: str) -> None:
        super().__init__(t, context)
        self.system: str = system


class InterventionEvent(SystemEvent):
    def __init__(self, context: Context, system: str, *data: _Any) -> None:
        super().__init__("INTERVENTION", context, system)
        self.data: tuple[_Any, ...] = data


class InterventionExitEvent(InterventionEvent):
    pass


class SuspensionEvent(SystemEvent):
    def __init__(self, context: Context, system: str, cause: str, fatal: bool = False) -> None:
        super().__init__("SUSPENSION", context, system)
        self.cause: str = cause
        self.fatal: bool = fatal


class EventListener(CallbackChain):
    @_override
    def super(self, e: Event) -> None:
        super().super(e)

    def pre_push(self, event: DataPushedEvent) -> None: ...

    def post_push(self, event: DataPushedEvent) -> None: ...

    def on_update(self, event: UpdateEvent) -> None: ...

    def pre_intervene(self, event: InterventionEvent) -> None: ...

    def post_intervene(self, event: InterventionExitEvent) -> None: ...

    def pre_suspend(self, event: SuspensionEvent) -> None: ...

    def post_suspend(self, event: SuspensionEvent) -> None: ...

    def left_indicator(self, event: Event, state: bool) -> None: ...

    def right_indicator(self, event: Event, state: bool) -> None: ...

    def hazard(self, event: Event, state: bool) -> None: ...
